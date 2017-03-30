        mkt_quantity = floor(100 * strength)
        cur_quantity_l = self.current_positions[symbol+'_long']
        cur_quantity_s = self.current_positions[symbol+'_short']
        order_type = 'MKT'

        if signal_type == 'LONG':   # and cur_quantity == 0:
            order = OrderEvent(dt, signal_type,symbol, price,
                               order_type,
                               quantity_l = mkt_quantity,
                               quantity_s = 0, 'BUY')
        if signal_type == 'SHORT':  # and cur_quantity ==0:
            order = OrderEvent (dt, signal_type, symbol,price,
                                order_type,
                                quantity_l = 0,
                                quantity_s = mkt_quantity, 'SELL')

        if signal_type == 'EXITLONG' and cur_quantity_l > 0:
            order = OrderEvent(dt, signal_type, symbol,price,
                               order_type,
                               quantity_l = mkt_quantity,
                               quantity_s = 0, 'SELL')

        if signal_type == 'EXITSHORT' and cur_quantity_s > 0:
            order = OrderEvent(dt, signal_type, symbol, price,
                               order_type, mkt_quantity, 'BUY')


        # ALL LONG
        if signal_type == 'EXITALL':
            if cur_quantity_l > 0 and cur_quantity_s == 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = cur_quantity_l,
                                   quantity_s = 0, 'SELL')
        # ALL SHORT
        if signal_type == 'EXITALL':
            if cur_quantity_s > 0 and cur_quantity_l == 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = 0,
                                   quantity_s = cur_quantity_s,'BUY')
        # SHORT & LONG
        if signal_type == 'EXITALL':
            if cur_quantity_s > 0 and cur_quantity_l > 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = cur_quantity_l,
                                   quantity_s = cur_quantity_s,
                                   'BUY&SELL')
