# -*- coding: UTF-8 -*-
# tasks.py
#
# Copyright (C) 2014 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of MarMix.
#
# MarMix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MarMix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MarMix. If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import logging
from decimal import Decimal, getcontext

# Core Django imports
from django.utils.translation import ugettext as _

# Third-party app imports
from async_messages import messages
from celery.utils.log import get_task_logger

# MarMix imports
from config.celery import app
from simulations.models import Simulation


# Get an instance of a logger
logger = get_task_logger(__name__)


@app.task
def check_matching_orders(order_id):
    """
    Looks for matching orders in the order book.

    :param order: An order object
    :return : None
    """
    # TODO: Check if balance is sufficient!
    from .models import Order, process_order
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        order = None

    if order and order.stock.simulation.state == Simulation.RUNNING:
        logger.debug("Starting a new order matching cycle...")
        if order.order_type == Order.ASK:
            book_order_type = Order.BID
        else:
            book_order_type = Order.ASK
        logger.debug("Order type: %s" % book_order_type)
        if not order.price:
            logger.debug("No price asked, market order.")
            # This is a market order
            if book_order_type == Order.BID:
                order_book = Order.objects.filter(stock=order.stock).filter(state=Order.SUBMITTED).filter(order_type=book_order_type).filter(price__isnull=False).order_by('-price')
            else:
                order_book = Order.objects.filter(stock=order.stock).filter(state=Order.SUBMITTED).filter(order_type=book_order_type).filter(price__isnull=False).order_by('price')
            if order_book:
                logger.debug("We have limit orders in the book")
                qty = order.quantity
                for match_order in order_book:
                    if match_order.team != order.team:
                        if match_order.quantity >= qty:
                            #  We can fulfill the whole order
                            qty_traded = qty
                            logger.debug("Full order can be fulfilled: %s" % qty_traded)
                        else:
                            #  We fulfill a partial order
                            # TODO we should look for the next one
                            qty_traded = match_order.quantity
                            logger.debug("Partial order can be fulfilled: %s (order qty was: %s)" %
                                         (qty_traded, match_order.quantity))
                        if order.order_type == Order.ASK:
                            sell_order = order
                            buy_order = match_order
                        else:
                            sell_order = match_order
                            buy_order = order
                        logger.debug("Processing the order: SELL: %s / BUY: %s / QTY: %s" %
                                     (sell_order, buy_order, qty_traded))
                        process_order(order.stock.simulation, sell_order, buy_order, qty_traded)
                        logger.info("New transaction: STOCK: %s QTY: %s SELLER: %s BUYER: %s" % (order.stock, qty_traded, sell_order.team, buy_order.team))
                        break
        else:
            # This is a limit order
            logger.debug("Price asked, limit order.")
            order_book = Order.objects.filter(stock=order.stock).filter(state=Order.SUBMITTED).filter(order_type=book_order_type).filter(price__isnull=True).order_by('timestamp')
            if order_book:
                logger.debug("We have market orders in the book")
                qty = order.quantity
                for match_order in order_book:
                    if match_order.team != order.team:
                        if match_order.quantity >= qty:
                            #  We can fulfill the whole order
                            qty_traded = qty
                            logger.debug("Full order can be fulfilled: %s" % qty_traded)
                        else:
                            #  We fulfill a partial order and look for the next one
                            # TODO look for the next one
                            qty_traded = match_order.quantity
                            logger.debug("Partial order can be fulfilled: %s (order qty was: %s)" %
                                         (qty_traded, match_order.quantity))
                        if order.order_type == Order.ASK:
                            sell_order = order
                            buy_order = match_order
                        else:
                            sell_order = match_order
                            buy_order = order
                        logger.debug("Processing the order: SELL: %s / BUY: %s / QTY: %s" %
                                     (sell_order, buy_order, qty_traded))
                        process_order(order.stock.simulation, sell_order, buy_order, qty_traded)
                        logger.info("New transaction: STOCK: %s QTY: %s SELLER: %s BUYER: %s" % (order.stock, qty_traded, sell_order.team, buy_order.team))
                        break
            else:
                if book_order_type == Order.BID:
                    order_book = Order.objects.filter(stock=order.stock).filter(state=Order.SUBMITTED).filter(order_type=book_order_type).filter(price__isnull=False).order_by('-price')
                else:
                    order_book = Order.objects.filter(stock=order.stock).filter(state=Order.SUBMITTED).filter(order_type=book_order_type).filter(price__isnull=False).order_by('price')
                if order_book:
                    logger.debug("We have limit orders in the book")
                    qty = order.quantity
                    for match_order in order_book:
                        if order.order_type == Order.ASK:
                            sell_order = order
                            buy_order = match_order
                        else:
                            sell_order = match_order
                            buy_order = order
                        if match_order.team != order.team and sell_order.price <= buy_order.price:
                            if match_order.quantity >= qty:
                                #  We can fulfill the whole order
                                qty_traded = qty
                                logger.debug("Full order can be fulfilled: %s" % qty_traded)
                            else:
                                #  We fulfill a partial order and look for the next one
                                qty_traded = match_order.quantity
                                logger.debug("Partial order can be fulfilled: %s (order qty was: %s)" %
                                             (qty_traded, match_order.quantity))
                            logger.debug("Processing the order: SELL: %s / BUY: %s / QTY: %s" %
                                         (sell_order, buy_order, qty_traded))
                            process_order(order.stock.simulation, sell_order, buy_order, qty_traded)
                            logger.info("New transaction: STOCK: %s QTY: %s SELLER: %s BUYER: %s" % (order.stock, qty_traded, sell_order.team, buy_order.team))
                            break


@app.task
def set_stock_quote(stock_id, price):
    """
    Creates a new stock quote.

    :param stock: The stock
    :param price: The price of the last transaction
    :return: Quote object
    """
    from .models import Quote, Stock
    stock = Stock.objects.get(pk=stock_id)
    price = Decimal(price)
    new_quote = Quote(stock=stock, price=price)
    new_quote.save()
    stock.price = price
    stock.save()
    return new_quote


@app.task
def set_opening_price(stock_id, price):
    getcontext().prec = 4
    from .models import Stock, Transaction, TransactionLine
    stock = Stock.objects.get(pk=stock_id)
    transactions = TransactionLine.objects.filter(stock=stock, transaction__transaction_type=Transaction.INITIAL)
    price = Decimal(price)
    print("Setting the opening price: %s @ %s" % (stock.symbol, price))
    for transaction_line in transactions:
        amount = price * transaction_line.quantity
        transaction_line.amount = Decimal(amount)
        transaction_line.price = Decimal(price)
        transaction_line.save()


@app.task
def open_market(simulation_id):
    simulation = Simulation.objects.get(pk=simulation_id)
    for stock in simulation.stocks.all():
        open_market_stock.apply_async([stock.id])


@app.task
def open_market_stock(stock_id):
    from .models import Stock, Order
    stock = Stock.objects.get(pk=stock_id)
    market_orders = Order.objects.filter(stock_id=stock.id).filter(state=Order.SUBMITTED).filter(price__isnull=True).order_by('created_at')
    if market_orders:
        for order in market_orders:
            check_matching_orders(order.id)

