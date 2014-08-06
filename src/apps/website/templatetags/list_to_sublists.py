#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Template filters to partition lists into rows or columns.

A common use-case is for splitting a list into a table with columns::

    {% for prod_row in products|columns:3 %}
      <div class="row">
      {% for product in prod_row %}
        <div class="col-md-4">
          <div class="product border-gray" data-url="{% url 'website:product:product_detail' product.id %}">
            <div class="image">
              <img src="{{ product.title_image_url }}"/>
              <div class="image-caption"><div class="text">{{ product.name }}</div></div>
            </div>
            <div class="summary">
              <p>{{ product.summary }}</p>
              <div class="price">{{ product.price_text }}</div>
            </div>
          </div>
        </div>
      {% endfor %}
      </div>
    {% endfor %}
"""

from django.template import Library

register = Library()


def rows(the_list, n):
    """
    Break a list into ``n`` rows, filling up each row to the maximum equal
    length possible. For example::

        >>> l = range(10)

        >>> rows(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> rows(l, 3)
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

        >>> rows(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        >>> rows(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> rows(l, 9)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [], [], [], []]

        # This filter will always return `n` rows, even if some are empty:
        >>> rows(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        the_list = list(the_list)
    except (ValueError, TypeError):
        return [the_list]
    list_len = len(the_list)
    split = list_len // n

    if list_len % n != 0:
        split += 1
    return [the_list[split*i:split*(i+1)] for i in range(n)]


def rows_distributed(the_list, n):
    """
    Break a list into ``n`` rows, distributing columns as evenly as possible
    across the rows. For example::

        >>> l = range(10)

        >>> rows_distributed(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> rows_distributed(l, 3)
        [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> rows_distributed(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]

        >>> rows_distributed(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> rows_distributed(l, 9)
        [[0, 1], [2], [3], [4], [5], [6], [7], [8], [9]]

        # This filter will always return `n` rows, even if some are empty:
        >>> rows(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        the_list = list(the_list)
    except (ValueError, TypeError):
        return [the_list]
    list_len = len(the_list)
    split = list_len // n

    remainder = list_len % n
    offset = 0
    rows = []
    for i in range(n):
        if remainder:
            start, end = (split+1)*i, (split+1)*(i+1)
        else:
            start, end = split*i+offset, split*(i+1)+offset
        rows.append(the_list[start:end])
        if remainder:
            remainder -= 1
            offset += 1
    return rows


def columns(the_list, n):
    """
    Break a list into ``n`` columns, filling up each column to the maximum equal
    length possible. For example::

        >>> from pprint import pprint
        >>> for i in range(7, 11):
        ...     print '%sx%s:' % (i, 3)
        ...     pprint(columns(range(i), 3), width=20)
        7x3:
        [[0, 3, 6],
         [1, 4],
         [2, 5]]
        8x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5]]
        9x3:
        [[0, 3, 6],
         [1, 4, 7],
         [2, 5, 8]]
        10x3:
        [[0, 4, 8],
         [1, 5, 9],
         [2, 6],
         [3, 7]]

        # Note that this filter does not guarantee that `n` columns will be
        # present:
        >>> pprint(columns(range(4), 3), width=10)
        [[0, 2],
         [1, 3]]
    """
    try:
        n = int(n)
        the_list = list(the_list)
    except (ValueError, TypeError):
        return [the_list]
    list_len = len(the_list)
    split = list_len // n
    if list_len % n != 0:
        split += 1
    return [the_list[i::split] for i in range(split)]

register.filter(rows)
register.filter(rows_distributed)
register.filter(columns)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()