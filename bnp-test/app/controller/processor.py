# System imports
import xml.etree.ElementTree as ET
import pandas as pd
import logging
import sys

# Package imports
from xml.etree.ElementTree import ParseError

logger = logging.getLogger(__name__)


def validate_xml(xml):
    """Validate xml to check if it is well formatted and contains required attributes

    Parameters
    ----------
    xml : str
        input string in xml format

    Returns
    -------
    str
        output string, if properly formatted

    """
    logger.info("Validating xml...")
    try:
        root = ET.fromstring(xml)
        for child in root:
            if not('correlationid' in child.attrib
                    and 'numberoftrades' in child.attrib
                    and 'tradeid' in child.attrib
                    and 'limit' in child.attrib):
                msg = 'One or more required attributes not found! Exiting program!'
                logger.error(msg)
    except SyntaxError as e:
        msg = 'Malformed xml! Exiting program!'+format(str(e))
        logger.error(msg)
        sys.exit()
    else:
        logger.info("Valid xml!")
        return root


def get_trade_list_from_xml(xml):
    """Parse xml etree and extract trade data into list

    Parameters
    ----------
    xml : str
        input string in xml etree format

    Returns
    -------
    list
        list of trades, if values present in correct data type
    """
    logger.info('Getting trade list from xml...')
    trades = []
    for child in xml:
        correlation_id = child.get('correlationid')
        number_of_trades = child.get('numberoftrades')
        limit = child.get('limit')
        trade_id = child.get('tradeid')
        amount = child.text
        try:
            column = 'limit'
            limit = float(limit)
            column = 'amount'
            amount = float(amount)
            column = 'number_of_trades'
            number_of_trades = int(number_of_trades)
            ct = {'CorrelationId': correlation_id,
                  'NumberOfTrades': number_of_trades,
                  'Limit': limit,
                  'TradeID': trade_id,
                  'Amount': amount}
            trades.append(ct)
        except TypeError as e:
            msg = 'One or more columns in not in the correct data type [{}]'.format(column)
            logger.error(msg)
            sys.exit()
    logger.info('Trade list extracted. [{}] trades!'.format(str(len(trades))))
    return trades


def get_data_frame_from_list(t_list):
    """Prepare pandas data frame from list

    Parameters
    ----------
    t_list : list
        list of trades

    Returns
    -------
    dataframe
        pandas data frame

    """
    logger.info('Getting data frame from list...')
    df = pd.DataFrame(t_list)
    df.set_index('TradeID', drop=True, inplace=True)
    logger.info('Data frame formed!')
    return df


def process_data_frame(data_frame):
    """Process input pandas data frame

    After grouping by CorrelationId, State is calculated as follows:
    TotalAmount < Amount = Rejected;
    Number of trades > Max number of trades = Rejected;
    Number of trades < Max number of trades = Pending;
    Accepted in all other cases

    Parameters
    ----------
    data_frame : dataframe
        trade data dataframe

    Returns
    -------
    str
        trade data dataframe grouped by correlationid, in csv string format

    """
    logger.info('Form data frame groups...')
    dfg = data_frame.groupby('CorrelationId').agg(
        {'CorrelationId': 'count', 'NumberOfTrades': 'max', 'Amount': 'sum', 'Limit': 'max'})
    dfg = dfg.rename(columns={
        'CorrelationId': 'NumberOfTrades',
        'NumberOfTrades': 'MaxNumberOfTrades',
        'Amount': 'ActualTotalAmount'})

    def trade_state(row):
        if (row['NumberOfTrades'] > row['MaxNumberOfTrades']) \
                or (row['ActualTotalAmount'] > row['Limit']):
            val = 'Rejected'
        elif row['NumberOfTrades'] < row['MaxNumberOfTrades']:
            val = 'Pending'
        else:
            val = 'Accepted'
        return val

    dfg['State'] = dfg.apply(trade_state, axis=1)
    logger.info('Data frame groups formed. [{}] groups!'.format(str(len(dfg.index))))
    logger.info('Forming csv string...')
    csv = dfg.sort_index()[['NumberOfTrades', 'State']].to_csv()
    logger.info('CSV string formed!')
    return csv


