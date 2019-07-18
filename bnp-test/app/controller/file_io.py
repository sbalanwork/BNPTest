# System imports
import logging

logger = logging.getLogger(__name__)


def read_file(file):
    """Read input file into string

    Parameters
    ----------
    file : str
        file path

    Returns
    -------
    str
        file contents

    """
    logger.info('Reading input file...')
    try:
        with open(file,'r') as in_file:
            xml = in_file.read().lower()
    except FileNotFoundError as e:
        logger.error(str(e))
        raise FileNotFoundError
    except OSError as e:
        logger.error('Access-error on file "' + file + '"! \n' + str(e))
        raise OSError
    except:
        logger.error('Unable to read file')
        raise Exception('Unknown exception!')
    else:
        logger.info('Input file read successfully. [{}] lines!'.format(str(len(xml.split('\n')))))
        return xml


def write_file(file, content):
    """Write contents into file

    Parameters
    ----------
    file : str
        file name
    content : str
        file content

    Returns
    -------

    """
    logger.info('Writing output...')
    try:
        with open(file,'w', newline='') as out_file:
            out_file.write(content)
            logger.info('Output written successfully!')
    except OSError as e:
        logger.error('Access-error on file "' + file + '"! \n' + str(e))
        raise OSError
    except:
        logger.error('Unable to write file')
        raise Exception('Unknown error')
