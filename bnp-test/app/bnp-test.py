# System imports
import sys
import logging

# Local imports
from controller import processor, file_io


def process_file(file):
    """Main entry point into package.

    Called from the init function with the input file supplied as an argument.
    Each step is called from within it.

    Parameters
    ----------
    file : string
        The filename full path

    Returns
    -------

    """
    xml = file_io.read_file(file)
    xml_valid = processor.validate_xml(xml)
    trades = processor.get_trade_list_from_xml(xml_valid)
    data_frame = processor.get_data_frame_from_list(trades)
    csv = processor.process_data_frame(data_frame)
    file_io.write_file('results.csv', csv)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='server.log', format='%(asctime)s,%(name)s,%(levelname)s,%(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p', level='INFO')
    logger.info('Start processing...')
    try:
        file_name = sys.argv[1]
    except IndexError as e:
        logger.error('Input file not specified')
    else:
        process_file(file_name)
        logger.info('End processing!')

