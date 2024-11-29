import argparse
import asyncio
from aiopath import AsyncPath
import aioshutil
import logging


COLOR_BLUE = "\u001b[34m"
COLOR_GREEN = "\u001b[32m"
COLOR_RED = "\u001b[31m"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def read_folder(source_folder, output_folder):
    async for child in source_folder.iterdir(): 
        if await child.is_dir():
            await read_folder(child, output_folder)
        elif await child.is_file():
            await copy_file(child, output_folder)


async def read_folder(source_folder, output_folder):
    try:
        tasks = []
        async for child in source_folder.iterdir():
            if await child.is_dir():
                tasks.append(read_folder(child, output_folder))
            elif await child.is_file():
                tasks.append(copy_file(child, output_folder))
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"read folder error: {e}")


async def copy_file(file, output_folder):
    destination_folder = output_folder/file.suffix.lower()
    await destination_folder.mkdir(parents=True, exist_ok=True)

    try:
        await aioshutil.copy(file, destination_folder)
        logging.info(COLOR_BLUE + f"Copied {file.name} to {destination_folder}.")
    except Exception as e:
        logging.error(COLOR_RED + f"Error copying {file.name}: {e}")


async def main():
    parser = argparse.ArgumentParser(description="Copy and organize files based on file extensions.")
    parser.add_argument("source_folder", type=AsyncPath, help="Source directory path")
    parser.add_argument("output_folder", nargs="?", type=AsyncPath, default=None, help="Destination directory path (default: 'dist' in the source directory)")
    args = parser.parse_args()

    if args.output_folder is None:
        args.output_folder = args.source_folder / "dist"

    try:
        await args.output_folder.mkdir(parents=False, exist_ok=True)
        await read_folder(args.source_folder, args.output_folder)
        logging.info(COLOR_GREEN + "Sorting files into folders has been completed successfully.")
    except Exception as e:
        logging.error(COLOR_RED + f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())       
