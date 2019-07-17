#!/usr/bin/env python
"""
dAbot by Kishan Bagaria

https://kishan-bagaria.deviantart.com/
https://kishanbagaria.com/

Usage:
  dAbot <username> <password> [-v] llama      give          random        (deviants|groups|exchangers)
  dAbot <username> <password> [-v] llama      give          msgs          (activity|replies)           [--trash_msgs]
  dAbot <username> <password> [-v] llama      give          file          (dev_names|dev_ids)          <file_path>
  dAbot <username> <password> [-v] llama      give          group_members <group>                      [--reversed]
  dAbot <username> <password> [-v] llama      give          url           <url>
  dAbot <username> <password> [-v] llama      give          traders
  dAbot <username> <password> [-v] llama      give          traders_random
  dAbot <username> <password> [-v] llama      give          <deviant>
  dAbot <username> <password> [-v] points     give          <deviant>     <amount>                     [<message>]
  dAbot <username> <password> [-v] points     balance
  dAbot <username> <password> [-v] devwatch   (add|remove)  <deviant>
  dAbot <username> <password> [-v] msgs       trash         (activity|bulletins|notices|replies|comments)
  dAbot <username> <password> [-v] comment    <deviant>     <comment>
  dAbot <username> <password> [-v] logout
  dAbot <username> <password> [-v] exec       <code>
  dAbot <username> <password> [-v] llama      stats         <deviant>
  dAbot <username> <password> [-v] llama      hof           group         <group_name> [--reversed]
  dAbot <username> <password> [-v] llama      hof           file          <file_path>
  dAbot <username> <password> [-v] llama      hof           <deviant_names>...
  dAbot <username> <password> [-v] badges     hof           <deviant_names>...
  dAbot <username> <password> [-v] save       random        (deviants|groups|exchangers)               <quantity>
  dAbot <username> <password> [-v] save       group_members <group>
  dAbot <username> <password> [-v] save       dev_ids       <dev_names_file_path>                      [--if_llama_given]
"""

from __future__ import division

try:
    import sets
except ImportError:
    pass
try:
    input = raw_input
except NameError:
    pass
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from urlparse import urlparse
except ImportError:
    import urllib.parse
try:
    from httplib import HTTPException
except ImportError:
    from http.client import HTTPException

import sys
IS_PYTHON_3 = sys.version_info >= (3, 0)

def except_hook(type, value, traceback):
    sys.__excepthook__(type, value, traceback)
    input('Press any key to exit...\n')

sys.excepthook = except_hook
sys.dont_write_bytecode = True

import os
import re
import time
import json
import atexit
import ctypes
import signal
import urllib
import datetime
import random
import bz2
import socket
import pprint

import requests
from requests.exceptions import RequestException
from dateutil.relativedelta import relativedelta
from retrying import retry
from docopt import docopt
from colorama import Fore, Back, Style
import colorama
colorama.init()

regex = {
    'received_llama_count' : '<td class="f">Received:</td><td class="f">([\d,]+|No).+?</td>',
    'given_llama_count'    : '<td class="f">Given:</td><td class="f">([\d,]+|No).+?</td>',
    'badges_count'         : '([\d,]+|No) Badges sent, ([\d,]+|No) Badges received',
    'points_balance'       : 'data-balance="([\d,]+)"',
    'dev_names'            : r'www\.deviantart\.com/([A-Za-z0-9-]+)',
    'llama_dev_name'       : 'Give a <strong>Llama Badge</strong> to <.+>([A-Za-z0-9-]+)<.+>\?',
    'llama_type'           : r'You have given\s+a\s+([a-zA-Z ]+?)\s+Badge\s+to',
    'llama_error_msg'      : '<li class="field_error".*?>(.+)</li>',
    'give_menu_json_dev_id': r'data-userid=\\"(\d+?)\\"',
    'llama_page_dev_id'    : 'gmi-gruser_id="(\d+)"',
    'llama_traders'        : r"Badges\.buildModal\(\\'llama\\', (\d+), (\d+)\)",
    'msg_center_id'        : '"folderid":"(\d+)"',
    'msg_class'            : '"msgclass":"([a-z_]+)"',
    'msg_count'            : '{"matches":"(\d+)"',
    'activity_msg_dev_ids' : '"msgid":"([\d]+:[\d]+:([\d]+):[\d]+)"',
    'validate_token'       : '<input .*?name="validate_token" .*?value="([a-z0-9]+)"',
    'validate_key'         : '<input .*?name="validate_key" .*?value="([0-9]+)"',
    'title'                : '<title>(.+?)</title>',
    'devname_title'        : '<title>(.+?)&#039;s badges.+</title>',
    'group_last_offset'    : '\.\.\.</a></li><li class="number"><a class="away" data-offset="(\d+)"',
    'user_comment_time'    : 'User Comments.+?<span class="side">(.+?)</span>'
}

url = {
    'badges_page'         : 'https://%s.deviantart.com/badges/',
    'llama_page'          : 'https://%s.deviantart.com/badges/llama/',
    'group_member_list'   : 'https://%s.deviantart.com/modals/memberlist/?offset=%d',
    'activity'            : 'https://%s.deviantart.com/activity/',
    'me_profile'          : 'https://me.deviantart.com/',
    'llama_trade'         : 'https://llamatrade.deviantart.com/',
    'random'              : 'https://www.deviantart.com/random/',
    'login_ref'           : 'https://www.deviantart.com/users/loggedin',
    'difi_get'            : 'https://www.deviantart.com/global/difi/?t=json&c[]=',
    'difi_post'           : 'https://www.deviantart.com/global/difi/',
    'points'              : 'https://www.deviantart.com/account/points/',
    'llama_give'          : 'https://www.deviantart.com/modal/badge/give?badgetype=llama&referrer=https://deviantart.com&to_user=',
    'process_trade'       : 'https://www.deviantart.com/modal/badge/process_trade',
    'process_trade_ref'   : 'https://www.deviantart.com/',
    'msg_center'          : 'https://www.deviantart.com/notifications/',
    'login'               : 'https://www.deviantart.com/users/login',
    'logout'              : 'https://www.deviantart.com/users/logout'
}

printed_dates = []
def get_datetime_now():
    now = datetime.datetime.utcnow()
    date = '{0:%d} {0:%b} {0:%Y}'.format(now)
    if not date in printed_dates:
        printed_dates.append(date)
        print(Style.BRIGHT + date + Style.RESET_ALL)
    return '{0:%I}:{0:%M}:{0:%S}.{1:03d} {0:%p}'.format(now, now.microsecond // 1000)

def echo(message):
    print(Style.BRIGHT + get_datetime_now() + '   ' + message + Style.RESET_ALL)

def log(file_name, text):
    with open(file_name, 'ab') as f:
        f.write(text.encode('utf-8'))

attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
def human_readable(delta):
    for attr in attrs:
        if getattr(delta, attr):
            yield '%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
def human_readable_file_size(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def wait(seconds):
    waiting_text = ' | Waiting %s' % ' '.join(human_readable(relativedelta(seconds=seconds)))
    console.title += waiting_text
    time.sleep(seconds)
    console.title = console.title.replace(waiting_text, '')

def get_relative_time_in_mins(relative_time):
    total_minutes = 0
    for m in re.finditer('(\d+) (year|month|week|day|hour|minute)', relative_time):
        total_minutes += int(m.group(1)) * {'minute': 1,
                                            'hour'  : 60,
                                            'day'   : 60 * 24,
                                            'week'  : 60 * 24 * 7,
                                            'month' : 60 * 24 * 30,
                                            'year'  : 60 * 24 * 365}[m.group(2)]
    return total_minutes

def get_validate_token(html):
    r = re.search(regex['validate_token'], html)
    if not r:
        print(html)
    return r.group(1)

def get_validate_key(html):
    r = re.search(regex['validate_key'], html)
    if not r:
        print(html)
    return r.group(1)

def get_title(html):
    return re.search(regex['title'], html).group(1)

def get_redirected_url(url):
    return req.head(url).headers['Location']

def get_random(what):
    parsed = urlparse.urlparse(get_redirected_url(url['random'] + what))
    return parsed.hostname.split('.')[0]

def get_dev_id(dev_name):
    dev_name = dev_name.lower()
    difi_json = difi_unauth_get('"User","getGiveMenu",["%s"]' % dev_name)
    dev_id = re.search(regex['give_menu_json_dev_id'], difi_json).group(1)
    return dev_id

def login(username, password):
    echo('Downloading login page')
    login_html = dA.get(url['login']).text
    params = {
        'ref'            : url['login_ref'],
        'username'       : username,
        'password'       : password,
        'remember_me'    : 1,
        'validate_token' : get_validate_token(login_html),
        'validate_key'   : get_validate_key(login_html)
    }
    echo('Logging in as %s' % username)
    post = dA.post(url['login'], data=params)
    post_html = post.text
    if '"loggedIn":true' in post_html:
        echo('Logged in as ' + username)
        return True
    else:
        log('login_error.htm', post_html)
        echo(Back.RED + post.url)

def is_logged_in(username):
    echo('Checking if logged in as ' + username)
    return dA.head(url['me_profile']).headers.get('Location').lower() == 'https://' + username.lower() + '.deviantart.com/'

def logout():
    echo('Logging out %s from all sessions' % username)
    dA.post(url['logout'])

def validate_response(difi_json, cParam):
    if '"response":{"status":"SUCCESS"' not in difi_json:
        if 'DiFi' in difi_json:
            difi_json = json.dumps(json.loads(difi_json)['DiFi'], indent=2)
        echo(Fore.RED + 'DiFi ' + cParam + ' Failed:' + Style.RESET_ALL + Back.RED + '\n' + difi_json)
    return difi_json

def _difi_get(req, cParam):
    return validate_response(req.get(url['difi_get'] + cParam).text, cParam)

def difi_get(cParam):
    return _difi_get(dA, cParam)

def difi_unauth_get(cParam):
    return _difi_get(requests, cParam)

def difi_post(cParam):
    params = {
        'ui'  : urllib.unquote(dA.cookies['userinfo']),
        'c[]' : cParam,
        't'   : 'json'
    }
    return validate_response(dA.post(url['difi_post'], data=params).text, cParam)

def get_points_balance():
    return int(re.search(regex['points_balance'], dA.get(url['points']).text).group(1))

def echo_points_balance():
    return echo(Fore.GREEN + 'Points: %d' % get_points_balance())

def get_last_user_comment_time(dev_name):
    activity_html = dA.get(url['activity'] % dev_name).text
    if 'User Comments' in activity_html:
        relative_time = re.search(regex['user_comment_time'], activity_html, re.DOTALL).group(1)
        return relative_time
    else:
        echo(Fore.RED + re.search(regex['title'], activity_html).group(1))

def get_llama_stats(dev_name):
    llama_html = req.get(url['llama_page'] % dev_name).text
    if 'Llamas are awesome!' not in llama_html:
        return {'Received': 0, 'Given': 0}
    received_count = re.search(regex['received_llama_count'], llama_html).group(1).replace(',', '')
    given_count = re.search(regex['given_llama_count'], llama_html).group(1).replace(',', '')
    dev_name = re.search(regex['devname_title'], llama_html).group(1)
    if received_count == 'No' : received_count = 0
    if given_count    == 'No' : given_count    = 0
    return {'Received': int(received_count), 'Given': int(given_count), 'HTML': llama_html, 'Name': dev_name}

def get_badges_stats(dev_name):
    badges_html = req.get(url['badges_page'] % dev_name).text
    counts = re.search(regex['badges_count'], badges_html)
    dev_name = re.search(regex['devname_title'], badges_html).group(1)
    given_count = counts.group(1).replace(',', '')
    received_count = counts.group(2).replace(',', '')
    if received_count == 'No' : received_count = 0
    if given_count    == 'No' : given_count    = 0
    return {'Received': int(received_count), 'Given': int(given_count), 'HTML': badges_html, 'Name': dev_name}

def echo_llama_stats(dev_name):
    counts = get_llama_stats(dev_name)
    echo(Back.RED    + dev_name + ' Llama Badge Stats')
    echo(Fore.GREEN  + 'Received:   %10d Llamas' % counts['Received'])
    echo(Fore.YELLOW + 'Given:      %10d Llamas' % counts['Given'])
    echo(Fore.RED    + 'Difference: %10d Llamas' % (counts['Received'] - counts['Given']))

def echo_llamalist_stats(dev_names, badges=False, proof=True):
    stats = {}
    for dev_name in dev_names:
        counts = get_llama_stats(dev_name) if not badges else get_badges_stats(dev_name)
        dev_name = counts.get('Name')
        if not dev_name: continue
        stats[dev_name] = counts
        print('@{} {:,} badges sent, {:,} badges received'.format(dev_name, counts['Given'], counts['Received']))
    print(Fore.GREEN + '---' + Style.RESET_ALL)
    num = 1
    #+k[1]['Received']
    for dev_name, counts in sorted(stats.items(), key=lambda k: k[1]['Given'], reverse=True):
        if proof:
            print('{}. @{} {:,} badges sent, {:,} badges received <a href="https://{}.deviantart.com/badges/{}">[proof]</a><br>'
              .format(num, dev_name, counts['Given'], counts['Received'], dev_name, '' if badges else 'llama/'))
        else:
            print('{}. @{} {:,} badges sent, {:,} badges received<br>'
              .format(num, dev_name, counts['Given'], counts['Received']))
        num += 1

def get_dev_names(text):
    for deviant in set(re.findall(regex['dev_names'], text)):
        yield deviant

llama_counts = {
    'success'      : 0,
    'already'      : 0,
    'cannot'       : 0,
    'expired'      : 0,
    'unknown'      : 0,
    'not_exchanger': 0
}
wait_enabled = False
def give_llama(dev_id, trade_id=''):
    global wait_enabled
    give_html = dA.get(url['llama_give'] + dev_id).text
    if 'Server Too Busy' in give_html:
        give_llama(dev_id, trade_id)
    dev_name = re.search(regex['llama_dev_name'], give_html)
    if dev_name:
        dev_name = dev_name.group(1)
    params = {
        'validate_token'      : get_validate_token(give_html),
        'validate_key'        : get_validate_key(give_html),
        'trade_id'            : trade_id,
        'to_user'             : dev_id,
        'referrer'            : url['process_trade_ref'],
        'quantity'            : '1',
        'password_remembered' : '1',
        'tos'                 : '1',
        'badgetype'           : 'llama'
    }
    process_html = dA.post(url['process_trade'], data=params).text
    if 'Badges have been given too quickly, and have tripped a spam filter.' in process_html:
        echo(Fore.RED + 'Spam Filter')
        if trade_id == '':
            wait_enabled = True
            wait(SPAM_FILTER_START_WAIT)
        give_llama(dev_id, trade_id)
    elif ("Problem securing Points; try again?"      in process_html or
          "You don't have enough Points to do that." in process_html or
          "Server Too Busy"                          in process_html):
        give_llama(dev_id, trade_id)
    elif 'You have given' in process_html:
        LlamaTransactions.add(dev_name.lower())
        badge_type = re.search(regex['llama_type'], process_html)
        if badge_type:
            badge_type = badge_type.group(1)
        llama_counts['success'] += 1
        llama_counts[badge_type] = llama_counts.get(badge_type, 0) + 1
        echo(Fore.GREEN + '{:<5} {:<22} {:<14} {:<10}'.format(llama_counts['success'], dev_name, badge_type, dev_id))
        if trade_id == '' and wait_enabled:
            wait(SPAM_FILTER_EACH_WAIT)
    elif 'You cannot give any more llama badges to ' in process_html:
        LlamaTransactions.add(dev_name.lower())
        echo_llama_already_given(dev_name, dev_id)
    elif 'Cannot give badge to this user' in process_html:
        llama_counts['cannot'] += 1
        echo(Fore.RED + '{:<5} {:<22} {}'.format(llama_counts['cannot'], dev_name, dev_id))
    elif 'That trade offer no longer exists.' in process_html or 'That trade offer has expired.' in process_html:
        llama_counts['expired'] += 1
        echo(Fore.CYAN + '{:<5} {:<22} {}'.format(llama_counts['expired'], dev_name, dev_id))
    else:
        llama_counts['unknown'] += 1
        echo(Back.RED + '{:<5} {:<22} {}'.format(llama_counts['unknown'], dev_name, dev_id))
        log('{} {} {} {}.htm'.format(get_datetime_now().replace(':', '.'), dev_id, dev_name, trade_id), process_html)
        error_msg = re.search(regex['llama_error_msg'], process_html)
        if error_msg:
            echo(Back.RED + error_msg.group(1))

def echo_llama_already_given(dev_name, dev_id=''):
    llama_counts['already'] += 1
    echo(Fore.YELLOW + '{:<5} {:<22} {}'.format(llama_counts['already'], dev_name, dev_id))

def get_dev_id_if_llama_not_given(dev_name):
    dev_name = dev_name.lower()
    if dev_name in LlamaTransactions:
        return echo_llama_already_given(dev_name)
    difi_json = difi_get('"User","getGiveMenu",["%s"]' % dev_name)
    if 'Already gave a Llama' in difi_json or 'Has Llamas enough for love' in difi_json:
        LlamaTransactions.add(dev_name)
        echo_llama_already_given(dev_name)
    else:
        m = re.search(regex['give_menu_json_dev_id'], difi_json)
        if m: return m.group(1)

def give_llama_to_deviant(dev_name):
    dev_id = get_dev_id_if_llama_not_given(dev_name)
    if dev_id: give_llama(dev_id)

def give_llama_if_exchanger(dev_name):
    stats    = get_llama_stats(dev_name)
    if stats['Given'] > stats['Received']:
        dev_id = re.search(regex['llama_page_dev_id'], stats['HTML']).group(1)
        give_llama(dev_id)
    else:
        llama_counts['not_exchanger'] += 1
        echo(Fore.MAGENTA + '{:<5} {:<22} {:<5} {:<5} {:<5}'.format(llama_counts['not_exchanger'],
                                                                    dev_name,
                                                                    stats['Received'],
                                                                    stats['Given'],
                                                                    stats['Received'] - stats['Given']))

def give_llama_to_activity_msgs_deviants(trash_msgs=False):
    difi_json = get_msgs('fb_activity')
    msg_class = re.search(regex['msg_class'], difi_json).group(1)
    for msg in re.finditer(regex['activity_msg_dev_ids'], difi_json):
        msg_id = msg.group(1)
        dev_id = msg.group(2)
        give_llama(dev_id)
        if trash_msgs:
            trash_msg(msg_class + ':' + msg_id)

def trade_llamas():
    trade_html = dA.get(url['llama_trade']).text
    for trade in re.finditer(regex['llama_traders'], trade_html):
        give_llama(trade.group(1), trade_id=trade.group(2))
def trade_llamas_alt():
    badges_url = url['badges_page'] % get_random('deviant')
    trade_html = dA.get(badges_url).text
    for trade in re.finditer(regex['llama_traders'], trade_html):
        give_llama(trade.group(1), trade_id=trade.group(2))

_msg_center_id = None
def get_msg_center_id():
    global _msg_center_id
    if not _msg_center_id:
        msg_center_html = dA.get(url['msg_center']).text
        _msg_center_id = re.search(regex['msg_center_id'], msg_center_html).group(1)
    return _msg_center_id

def get_msgs_page(msg_class, from_no):
    echo(Fore.GREEN + 'Getting {} messages from {} to {}'.format(msg_class, from_no, from_no + 120))
    return difi_get('"MessageCenter","get_views",["%s","oq:%s:%s:120:f"]' % (get_msg_center_id(), msg_class, from_no))

def get_msgs(msg_class):
    json = get_msgs_page(msg_class, 0)
    count = re.search(regex['msg_count'], json)
    if count:
        for i in xrange(120, int(count.group(1)), 120):
            json += get_msgs_page(msg_class, i)
    else:
        echo(Fore.YELLOW + 'No {} messages found!'.format(msg_class))
    return json

def get_group_members(group_name, reversed=False):
    html           = req.get(url['group_member_list'] % (group_name, 0)).text
    end_offset     = int(re.search(regex['group_last_offset'], html).group(1))
    reversed_offsets = xrange(end_offset, 0, -100)
    offsets          = xrange(0, end_offset, 100)
    for offset in (reversed_offsets if reversed else offsets):
        if offset != 0:
            html = req.get(url['group_member_list'] % (group_name, offset)).text
        echo(Fore.GREEN + "Downloaded %s's member list from offset %d" % (group_name, offset))
        for d in get_dev_names(html):
            yield d

def trash_msg(msg_id):
    echo(Fore.GREEN + 'Trashing message #' + msg_id)
    difi_post('"MessageCenter","trash_messages",["%s","id:%s"]' % (get_msg_center_id(), msg_id))

def trash_msg_class(msg_class):
    echo(Fore.GREEN + 'Trashing message class ' + msg_class)
    difi_post('"MessageCenter","trash_messages",["%s","uq:%s"]' % (get_msg_center_id(), msg_class))

def profile_comment(dev_name, comment, dev_id=None):
    if not dev_id:
        dev_id = get_dev_id(dev_name)
    echo(Fore.GREEN + 'Commenting "%s" on %s\'s profile page' % (comment, dev_name))
    difi_post('"Comments","post",["%s","%s","0","4","0"]' % (comment, dev_id))

def watch_deviant(dev_name):
    echo(Fore.GREEN + '+devWatching ' + dev_name)
    difi_post('"Friends","addFriendGetAttributes",["%s","devwatch-editor"]' % dev_name)

def unwatch_deviant(dev_name):
    echo(Fore.GREEN + '-devWatching ' + dev_name)
    difi_post('"Friends","removeFriend",["%s"]' % dev_name)

def change_devwatch_group(dev_name, group_id):
    echo(Fore.GREEN + 'Adding %s to group #%s' % (dev_name, group_id))
    difi_post('"Friends","addToGroup",["%s","%s"]' % (get_dev_id(dev_name), group_id))

def change_devwatch_attr(dev_name, attr):
    echo(Fore.GREEN + "Changing %s's watch attributes to %s" % (dev_name, attr))
    difi_post('"Friends","setAttributes",["%s","%s"]' % (get_dev_id(dev_name), attr))

def give_points(dev_name, amount, message=None):
    if not message: message = ''
    echo(Fore.GREEN + 'Are you sure you want to give %s points to %s?' % (amount, dev_name))
    ans = input('--> ')
    if ans == 'y':
        echo(Fore.GREEN + 'Giving...')
        difi_post('"Points","transferModal",["%s","%s","%s","%s","1"]' % (dev_name, amount, message, globals()['password']))

total_responses = 0
total_downloaded_bytes = 0
total_uploaded_bytes = 0
total_downloaded_content = 0
started_time = datetime.datetime.utcnow()

def print_stats():
    if not print_stats.printed:
        echo('')
        pprint.pprint(llama_counts)
        echo('[Llama Transactions] +%d' % (len(LlamaTransactions) - print_stats.transactions_count))
        echo('[Llama Transactions] %d' % len(LlamaTransactions))
        echo('[Network Stats]')
        echo('  Responses from Server:           %10d' % total_responses)
        echo('  Bytes Downloaded:                %10s' % human_readable_file_size(total_downloaded_bytes))
        echo('  Bytes Uploaded:                  %10s' % human_readable_file_size(total_uploaded_bytes))
        echo('  Bytes Downloaded (uncompressed): %10s' % human_readable_file_size(total_downloaded_content))
        print_stats.printed = True
print_stats.printed = False

def sigint_handler(signum, frame):
    print('')
    echo(Fore.RED + 'Exiting... [Ran %s]' % str(datetime.datetime.utcnow()-started_time))
    print_stats()
    sys.exit()

args = docopt(__doc__)
OS = [
    'Windows NT 6.3; WOW64',
    'Windows NT 6.3; Win64; x64',
    'Windows NT 6.2',
    'Windows NT 6.1',
    'Macintosh; Intel Mac OS X 10_10_3',
    'Macintosh; Intel Mac OS X 10_11_1',
    'Macintosh; Intel Mac OS X 10_12_6',
    'Macintosh; Intel Mac OS X 10_13_0'
]
USER_AGENTS = [
    'Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36',
    'Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Mozilla/5.0 (%s) Gecko/20100101 Firefox/51.0',
    'Mozilla/5.0 (%s) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (%s) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (%s) Gecko/20100101 Firefox/54.0'
]
SPAM_FILTER_START_WAIT = 60*30 # 30 minutes
SPAM_FILTER_EACH_WAIT = 0
LLAMA_TRADE_WAIT = 120

VERBOSE = args['-v']
username, password = args['<username>'], args['<password>']

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
DATA_DIRPATH = 'Data' if os.path.exists('Data') else os.path.expanduser('~/.dAbot')

COOKIES_DIRPATH = os.path.join(DATA_DIRPATH, 'Cookies')
TRANSACTIONS_DIR_PATH = os.path.join(DATA_DIRPATH, 'LlamaTransactions')
COOKIE_PATH = os.path.join(COOKIES_DIRPATH, username + '.pickle')
LLAMA_TRANSACTIONS_PATH = os.path.join(TRANSACTIONS_DIR_PATH, username + '.json.bz2')

def read_llama_transactions():
    if os.path.isfile(LLAMA_TRANSACTIONS_PATH):
        with bz2.BZ2File(LLAMA_TRANSACTIONS_PATH, 'r') as f:
            return set(json.load(f))
    return set()
def save_llama_transactions():
    with bz2.BZ2File(LLAMA_TRANSACTIONS_PATH, 'w') as f:
        json.dump(list(LlamaTransactions), f, separators=(',', ':'))
def read_cookies():
    if os.path.isfile(COOKIE_PATH):
        with open(COOKIE_PATH, 'rb') as f:
            dA.cookies = pickle.load(f)
def save_cookies():
    with open(COOKIE_PATH, 'wb') as f:
        pickle.dump(dA.cookies, f, pickle.HIGHEST_PROTOCOL)

def save_data():
    for d in [COOKIES_DIRPATH, TRANSACTIONS_DIR_PATH]:
        if not os.path.exists(d):
            os.makedirs(d)
    save_cookies()
    LlamaTransactions.update(read_llama_transactions())
    save_llama_transactions()
    print_stats()

def load_data():
    global LlamaTransactions
    if VERBOSE:
        echo('Data Directory Path: %s' % DATA_DIRPATH)
    read_cookies()
    LlamaTransactions = read_llama_transactions()
    print_stats.transactions_count = len(LlamaTransactions)
    echo('[Llama Transactions] %d' % len(LlamaTransactions))

signal.signal(signal.SIGINT, sigint_handler)

if sys.platform == 'win32':
    from console import console, CONSOLAS
    console.title = 'dAbot'
    @retry(stop_max_attempt_number=5)
    def set_console():
        console.font = CONSOLAS
        c = console.get_largest_window_size()
        w = (c.X // 2) - 4
        h = c.Y - 1
        console.set_buffer_size(width=w, height=32766)
        console.set_window_info(width=w, height=h)
    # execution stops after max attempts
    try:
        set_console()
    except:
        pass
else:
    class Console(object):
        @property
        def title(self):
            return self._title
        @title.setter
        def title(self, value):
            sys.stdout.write('\x1b]2;%s\x07' % value)
            self._title = value
    console = Console()

def header_size(headers):
    return sum(len(key) + len(value) + 4 for key, value in headers.items()) + 2

def response_hook(r, *args, **kwargs):
    global total_downloaded_bytes, total_uploaded_bytes, total_downloaded_content, total_responses
    request_line_size = len(r.request.method) + len(r.request.path_url) + 12
    response_line_size = len(r.reason) + 15
    request_size = request_line_size + header_size(r.request.headers) + int(r.request.headers.get('content-length', 0))
    response_size = response_line_size + header_size(r.headers) + int(r.headers.get('content-length', 0))
    total_downloaded_content += len(r.content)
    total_downloaded_bytes   += response_size
    total_uploaded_bytes     += request_size
    total_responses          += 1
    if VERBOSE:
        print(r.status_code, r.request.method, human_readable_file_size(response_size), human_readable_file_size(request_size), r.url)
    if r.status_code == 403 or r.status_code == 500 or 'The server could not complete your request' in r.text:
        raise DAThrottlingError(response=r)

class DAThrottlingError(RequestException):
    """DA server throttling request."""

def retry_if_network_error(exception):
    pick_da_useragent()
    do_retry = isinstance(exception, (requests.exceptions.RequestException, httplib.HTTPException, socket.error))
    if do_retry:
        echo(Fore.YELLOW + 'Retrying... ' + repr(exception))
    return do_retry

def pick_da_useragent():
    dA.headers['User-Agent'] = random.choice(USER_AGENTS) % random.choice(OS)
    if VERBOSE:
        echo('[User-Agent] %s' % dA.headers['User-Agent'])

dA = requests.session()
req = requests.session()
PROXIED = False
for _ in [dA, req]:
    _.trust_env = False
    _.hooks = {'response': response_hook}
    _.headers['Accept'] = '*/*'
    _.headers['Accept-Encoding'] = 'gzip, deflate'
    _.headers['Accept-Language'] = 'en'
    if PROXIED:
        _.proxies = {
          'http': '127.0.0.1:8080',
          'https': '127.0.0.1:8080'
        }
        _.verify = False

LlamaTransactions = set()

def init():
    pick_da_useragent()
    # TODO
    if not IS_PYTHON_3: atexit.register(save_data)
    load_data()

@retry(wait_exponential_multiplier=1*60*1000, retry_on_exception=retry_if_network_error)
def run():
    login_required = not args['hof']
    if login_required:
        if not is_logged_in(username):
            if not login(username, password):
                sys.exit()
        else:
            echo('Already logged in as ' + username)
    else:
        echo('Skipping login')

    console.title = 'dAbot | ' + username

    if   args['llama']:
        if   args['give']:
            if   args['random']:
                if   args['deviants']:
                    while True: give_llama_to_deviant(get_random('deviant'))
                elif args['groups']:
                    while True: give_llama_to_deviant(get_random('group'))
                elif args['exchangers']:
                    while True: give_llama_if_exchanger(get_random('deviant'))
            elif args['msgs']:
                if   args['activity']:
                    give_llama_to_activity_msgs_deviants(args['--trash_msgs'])
                elif args['replies']:
                    for d in get_dev_names(get_msgs('fb_replies')):
                        give_llama_to_deviant(d)
            elif args['file']:
                with open(args['<file_path>']) as f:
                    lines = f.read().splitlines()
                echo(Fore.GREEN + '%d deviants' % len(lines))
                for i, d in enumerate(list(lines), 1):
                    if   args['devnames']: give_llama_to_deviant(d)
                    elif args['devids']:   give_llama(d)
                    lines.remove(d)
                    if i % 16 == 0:
                        with open(args['<file_path>'], 'w') as f:
                            f.write('\n'.join(lines))
            elif args['group_members']:
                for m in get_group_members(args['<group>'], args['--reversed']):
                    give_llama_to_deviant(m)
            elif args['url']:
                for m in get_dev_names(req.get(args['<url>']).text):
                    give_llama_to_deviant(m)
            elif args['traders']:
                last_echo = None
                while True:
                    if last_echo != datetime.date.today():
                        last_echo = datetime.date.today()
                        echo_points_balance()
                    trade_llamas()
                    wait(LLAMA_TRADE_WAIT)
            elif args['traders_random']:
                last_echo = None
                while True:
                    if last_echo != datetime.date.today():
                        last_echo = datetime.date.today()
                        echo_points_balance()
                    trade_llamas_alt()
                    wait(LLAMA_TRADE_WAIT)
            else:
                give_llama_to_deviant(args['<deviant>'])
        elif args['stats']:
            echo_llama_stats(args['<deviant>'])
        elif args['hof']:
            names = []
            if args['<group_name>']:
                for m in get_group_members(args['<group_name>'], args['--reversed']):
                    names.append(m)
                echo_llamalist_stats(names, proof=False)
            elif args['<file_path>']:
                with open(args['<file_path>']) as f:
                    lines = f.read().splitlines()
                echo(Fore.GREEN + '%d deviants' % len(lines))
                for m in lines:
                    names.append(m)
                echo_llamalist_stats(lines, proof=False)
            else:
                echo_llamalist_stats(args['<deviant_names>'])
    elif args['badges']:
        echo_llamalist_stats(args['<deviant_names>'], True)
    elif args['points']:
        if   args['balance']:
            echo_points_balance()
        elif args['give']:
            give_points(args['<deviant>'], args['<amount>'], args['<message>'])
    elif args['devwatch']:
        if   args['add']:    watch_deviant(args['<deviant>'])
        elif args['remove']: unwatch_deviant(args['<deviant>'])
    elif args['msgs']:
        if   args['activity']:  trash_msg_class('fb_activity')
        elif args['bulletins']: trash_msg_class('bulletins')
        elif args['notices']:   trash_msg_class('notices')
        elif args['replies']:   trash_msg_class('fb_replies')
        elif args['comments']:  trash_msg_class('comments')
    elif args['comment']:
        profile_comment(args['<deviant>'], args['<comment>'])
    elif args['logout']:
        logout()
    elif args['save']:
        if   args['group_members']:
            with open(args['<group>'] + ' Members.txt', 'w') as f:
                for m in get_group_members(args['<group>']):
                    f.write(m + '\n')
        elif args['dev_ids']:
            with open(args['<dev_names_file_path>']) as f:
                dev_names = f.read().splitlines()
            echo(Fore.GREEN + '%d deviants' % len(dev_names))
            dev_ids = []
            if os.path.isfile('devIDs.txt'):
                with open('devIDs.txt') as f:
                    dev_ids = f.read().splitlines()
            # list() is used to remove items while looping
            for i, d in enumerate(list(dev_names), 1):
                dev_id = get_dev_id_if_llama_not_given(d)
                if dev_id:
                    dev_ids.append(dev_id)
                    echo(Fore.GREEN + d)
                dev_names.remove(d)
                if i % 16 == 0:
                    with open(args['<dev_names_file_path>'], 'w') as f:
                        f.write('\n'.join(dev_names))
                    with open('devIDs.txt', 'w') as f:
                        f.write('\n'.join(dev_ids))
                    wait(5)
        elif   args['random']:
            quantity = args['<quantity>']
            if   args['deviants']:
                for _ in xrange(quantity): get_random('deviant')
            elif args['groups']:
                for _ in xrange(quantity): get_random('group')
            elif args['exchangers']:
                #for _ in xrange(quantity): give_llama_if_exchanger(get_random('deviant'))
                pass
    elif args['exec']:
        code = args['<code>']
        print(code)
        exec(code)

def main():
    init()
    run()

if __name__ == '__main__':
    main()