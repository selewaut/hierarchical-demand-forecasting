from pathlib import Path
import logging
import requests
from tqdm import tqdm
from dataclasses import dataclass, field
from typing import Tuple

# Logger.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Info:
    """
    Downloads data set intor directory
    groups (Tuple): Tuple of str groups.
    class_groups (Tuple): Tuple of dataclasses
    """
    class_groups: Tuple[dataclass]
    groups: Tuple[str] = field(init=False)

    def __post_init__(self):
        self.groups = tuple(cls_.__name__ for cls_ in self.class_groups)

    def get_group(self, group: str):
        """Gets dataclass of group"""
        if group not in self.groups:
            raise Exception(f'Unkonwn group {group}')
        return self.class_groups[self.groups.index(group)]

    def __getitem__(self, group: str):
        """Gets dataclass of group."""
        if group not in self.groups:
            raise Exception(f'Unknown group {group}')
        return self.class_groups[self.groups.index(group)]

    def __iter__(self):
        for group in self.groups:
            yield group, self.get_group(group)


def download_file(directory: str, source_url: str, decompress: bool = False) -> None:
    """
    Download data from source_ulr inside directory.
    Parameters
    ----------
    directory: str, Path
        Custom directory where data will be downloaded.
    source_url: str
        URL where data is hosted.
    decompress: bool
        Wheter decompress downloaded file. Default False.
    :param directory: str, Path: target directory to save dataset files
    :param source_url: URL hosting data.
    :param decompress: Whete ompress downlaoded file.
    :return:
    """
    if isinstance(directory, str):
        directory = Path(directory)
    # Generate target directory.
    directory.mkdir(parents=True, exist_ok=True)
    # extract file name from url by splitting with "/"
    filename = Path(source_url.split('/')[-1])

    # On Windows file must have only .zip in suffix
    if '.zip' in filename.suffix:
        filename = Path(filename).stem + ".zip"
    # Generate target directory
    filepath = Path(f'{directory}/{filename}')

    # Streaming, so we can iterate over the response.
    headers = {'User-Agent': 'Mozilla/5.0'}
    # Query dataset url
    r = requests.get(source_url, stream=True, headers=headers)
    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(filepath, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
            f.flush()
    t.close()

    if total_size != 0 and t.n != total_size:
        logger.error('ERROR, something went wrong downloading data')

    size = filepath.stat().st_size
    logger.info(f'Successfully downloaded {filename}, {size}, bytes.')

    if decompress:
        if '.zip' in filepath.suffix:
            import zipfile
            logger.info('Decompressing zip file...')
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(directory)
        else:
            from patoolib import extract_archive
            extract_archive(filepath, outdir=directory)
        logger.info(f'Successfully decompressed {filepath}')
