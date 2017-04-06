def generate_perfect_log(tlog,latest_bar_dict):

    # tlog = go.get_log()
    # start = go.get_equity_curve().index[0]
    # end = go.get_equity_curve().index[-1]
    # capital = go.initial_capital
    # symbol_dict = data.symbol_dict

    def get_exit_long_tlog(tlog):
        return tlog[(tlog['s_type'] == 'EXIT_ALL') | \
                    (tlog['s_type'] == 'EXIT_LONG')]

    def get_exit_short_tlog(tlog):
        return tlog[(tlog['s_type'] == 'EXIT_ALL') | \
                    (tlog['s_type'] == 'EXIT_SHORT')]

    def get_long_tlog(tlog):
        return tlog[(tlog['s_type'] == 'LONG')]

    def get_short_tlog(tlog):
        return tlog[(tlog['s_type'] == 'SHORT')]

    # tlog['PnL'] = 0
    ellog = get_exit_long_tlog(tlog)
    eslog = get_exit_short_tlog(tlog)
    llog = get_long_tlog(tlog)
    slog = get_short_tlog(tlog)

    td = {}
    td['ttlog'] = []
    td['left_long_df'] = pd.DataFrame()
    td['left_lqty'] = 0
    td['l_fix'] = 0
    td['left_short_df'] = pd.DataFrame()
    td['left_sqty'] = 0
    td['s_fix'] = 0


    # import itertools as it
    # c = it.count()
    def exit_generator(e):
        for i in range(len(e)):
            # datetime, s_type, price, qty
            yield {'datetime':e.index[i],
                   's_type':e['s_type'][i],
                   'price':e['price'][i],
                   'qty':e['qty'][i]}

    def ls_generator(ls):
        for i in range(len(ls)):
            yield {'datetime':ls.index[i],
                   'symbol':ls['symbol'][i],
                   's_type':ls['s_type'][i],
                   'price':ls['price'][i],
                   'qty':ls['qty'][i],
                   'cur_positions':ls['cur_positions'][i],
                   'cash':ls['cash'][i],
                   'total':ls['total'][i],
                  'PnL':ls['PnL'][i]}

    elg = exit_generator(ellog)
    esg = exit_generator(eslog)
    lg = ls_generator(llog)
    sg = ls_generator(slog)


    td['leqty'] = 0
    td['seqty'] = 0
    td['etype'] = 0
    td['edata'] = 0

    td['update_long'] = 0
    td['ldata'] = 0
    td['update_short'] = 0
    td['sdata'] = 0


    while True:
        try:
            if td['leqty'] == 0 :
                td['edata'] = elg.next()
                td['etype'] = td['edata']['s_type']
                td['leqty'] = td['edata']['qty']

            if td['update_long'] == 0:
                td['ldata'] = lg.next()

        except:
            print 'no!!!!'
            break
        else:
            # for long
            if td['etype'] == 'EXIT_LONG':
                if td['left_lqty'] != 0:
                    if td['left_lqty'] <= td['leqty']:
                        td['left_long_df']['PnL'] = td['left_lqty'] * td['edata']['price'] + td['l_fix']
                        td['ttlog'].append(td['left_long_df'])
                        # initialize
                        td['leqty'] = td['leqty'] - td['left_lqty']
                        td['left_long_df'] = pd.DataFrame()
                        td['left_lqty'] = 0
                        td['l_fix'] = 0
                        td['update_long'] = 0

                    else:
                        symbol = td['ldata']['symbol']
                        latest_price = data.latest_bar_dict[symbol][-1]
                        td['left_lqty'] = td['left_lqty'] - td['leqty']
                        td['l_fix'] = td['leqty'] * td['edata']['price'] + td['l_fix']
                        td['left_long_df']['PnL'] = td['l_fix'] + td['left_lqty'] * latest_price
                        # initialize
                        td['leqty'] = 0

                else:
                    if td['ldata']['qty'] <= td['leqty']:

                        td['ldata']['PnL'] = td['ldata']['qty'] * td['edata']['price']
                        td['leqty'] = td['leqty'] - td['ldata']['qty']
                        td['ttlog'].append(td['ldata'])

                        td['update_long'] = 0
                    else:
                        symbol = td['ldata']['symbol']
                        latest_price = data.latest_bar_dict[symbol][-1]
                        td['left_lqty'] = td['ldata']['qty'] - td['leqty']
                        td['l_fix'] = td['leqty'] * td['edata']['price']
                        td['ldata']['PnL'] = td['l_fix'] + td['left_lqty'] * latest_price
                        td['left_long_df'] = td['ldata']
                        # initialize
                        td['leqty'] = 0
                        td['update_long'] = 1

            # for all
            if td['etype'] == 'EXIT_ALL':
                # for long
                if td['left_lqty'] != 0:
                    td['left_long_df']['PnL'] = td['left_lqty'] * td['edata']['price'] + td['l_fix']
                    td['ttlog'].append(td['left_long_df'])
                    # initialize
                    td['leqty'] = td['leqty'] - td['left_lqty']
                    td['left_long_df'] = pd.DataFrame()
                    td['left_lqty'] = 0
                    td['l_fix'] = 0
                    td['update_long'] = 0


                if td['ldata']['datetime'] <= td['edata']['datetime']:
                    td['ldata']['PnL'] = td['ldata']['qty'] * td['edata']['price']
                    td['leqty'] = td['leqty'] - td['ldata']['qty']
                    td['ttlog'].append(td['ldata'])
                    td['update_long'] = 0

                else:
                    td['update_long'] = 1
                    td['leqty'] = 0

    # for short
    while True:
        try:
            if td['seqty'] == 0:
                td['edata'] = esg.next()
                td['etype'] = td['edata']['s_type']
                td['seqty'] = td['edata']['qty']

            if td['update_short'] == 0:
                td['sdata'] = sg.next()

        except :
            print 'no!!!!'
            break
        else:
            # for short
            if td['etype'] == 'EXIT_SHORT':

                if td['left_sqty'] != 0:

                    if td['left_sqty'] <= td['seqty']:
                        td['left_short_df']['PnL'] = td['left_sqty'] * td['edata']['price'] + td['s_fix']
                        td['ttlog'].append(td['left_short_df'])
                        # initialize
                        td['seqty'] = td['seqty'] - td['left_sqty']
                        td['left_short_df'] = pd.DataFrame()
                        td['left_sqty'] = 0
                        td['s_fix'] = 0
                        td['update_short'] = 0


                    else:
                        symbol = td['ldata']['symbol']
                        latest_price = data.latest_bar_dict[symbol][-1]
                        td['left_sqty'] = td['left_sqty'] - td['seqty']
                        td['s_fix'] = td['seqty'] * td['edata']['price'] + td['s_fix']
                        td['left_short_df']['PnL'] = td['s_fix'] + td['left_sqty'] * latest_price
                        # initialize
                        td['seqty'] = 0

                else:
                    if td['sdata']['qty'] <= td['seqty']:
                        td['sdata']['PnL'] = td['sdata']['qty'] * td['edata']['price']
                        td['seqty'] = td['seqty'] - td['sdata']['qty']
                        td['ttlog'].append(td['sdata'])

                        td['update_short'] = 0

                    else:
                        symbol = td['ldata']['symbol']
                        latest_price = data.latest_bar_dict[symbol][-1]
                        td['left_sqty'] = td['sdata']['qty'] - td['seqty']
                        td['s_fix'] = td['seqty'] * td['edata']['price']
                        td['sdata']['PnL'] = td['s_fix'] + td['left_sqty'] * latest_price
                        td['left_short_df'] = td['sdata']
                        # initialize
                        td['seqty'] = 0
                        td['update_short'] = 1

            # for all
            if td['etype'] == 'EXIT_ALL':

                if td['left_sqty'] != 0:
                    td['left_short_df']['PnL'] = td['left_sqty'] * td['edata']['price'] + td['s_fix']
                    td['ttlog'].append(td['left_short_df'])
                    # initialize
                    td['seqty'] = td['seqty'] - td['left_sqty']
                    td['left_short_df'] = pd.DataFrame()
                    td['left_sqty'] = 0
                    td['s_fix'] = 0
                    td['update_short'] = 0

                if td['sdata']['datetime'] <= td['edata']['datetime']:
                    td['sdata']['PnL'] = td['sdata']['qty'] * td['edata']['price']
                    td['seqty'] = td['seqty'] - td['sdata']['qty']
                    td['ttlog'].append(td['sdata'])
                    td['update_short'] = 0

                else:

                    td['update_short'] = 1
                    td['seqty'] = 0
    return td['ttlog']
