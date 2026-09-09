import asyncio
import os
import zipfile


class CompressionService:
    async def compress_file(
        self,
        input_path: str,
        output_path: str,
        filename: str,
    ):
        await asyncio.to_thread(
            self._compress_sync,
            input_path,
            output_path,
            filename,
        )
        return output_path

    def _compress_sync(
        self,
        input_path: str,
        output_path: str,
        filename: str,
    ):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with zipfile.ZipFile(
            output_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        ) as zip_file:
            zip_file.write(input_path, arcname=filename)