import pandas as pd
import functools
import gc
from delta_sdk.utils import logging

def chunked_dataframe_processor(chunk_size=100_000):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
            if len(df) <= chunk_size:
                return func(df, *args, **kwargs)

            chunks = [
                df[i:i + chunk_size] for i in range(0, len(df), chunk_size)
            ]
            processed_chunks = []

            for idx, chunk in enumerate(chunks):
                print(f"Processing chunk {idx + 1}/{len(chunks)}")
                processed = func(chunk.copy(), *args, **kwargs)
                processed_chunks.append(processed)
                del chunk
                del processed
                gc.collect()

            final_df = pd.concat(processed_chunks, ignore_index=True)
            return final_df
        return wrapper
    return decorator