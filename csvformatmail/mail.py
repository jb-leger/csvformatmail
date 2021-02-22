#!/usr/bin/python3

from email.mime.text import MIMEText
import argparse
import smtplib
import csvspoon
import os
import re
import sys
import subprocess
import textwrap
from getpass import getpass

import time


def read_template(fn):
    with open(fn) as f:
        template = "".join(l for l in f)
    return template


class Mail:
    def __init__(self, template, row, glob):
        self._text = ""
        self._header = {}
        header = True
        parser = re.compile("^([^:]+): (.*)$")
        formatted_mail = eval(f"f{template!r}", row, glob)
        for l in formatted_mail.splitlines():
            if header:
                m = parser.match(l)
                if m:
                    k, v = m.groups()
                    self._header[k] = v
            else:
                self._text += l + "\n"
            if not l and self._header:
                header = False
        lower_headers = set(h.lower() for h in self._header)
        if "from" not in lower_headers:
            raise TypeError('invalid mail, "From" header must be specified')
        if "to" not in lower_headers:
            raise TypeError('invalid mail, "To" header must be specified')
        if "subject" not in lower_headers:
            raise TypeError('invalid mail, "Subject" header must be specified')

    def __str__(self):
        ret = (
            "\n".join(f"{k}: {v}" for k, v in self._header.items())
            + "\n\n"
            + self._text
        )
        return ret

    def to_email(self):
        msg = MIMEText(self._text)
        for k, v in self._header.items():
            msg[k] = v
        return msg


class Mailer:
    def __init__(self, host="localhost", port=25, starttls=False, login=None, password=None):
        self._host = host
        self._port = port
        self._starttls = starttls
        self._login = login
        self._password = password
        self._mails = []

    def add_mail(self, mail):
        self._mails.append(mail)

    def send_mails(self, wait=0):
        if self._password is None:
            self._password = getpass(f"SMTP password for user {self._login}: ")
        ngroups = len(self._mails)//25+1
        for group in range(ngroups):
            mailserver = smtplib.SMTP(self._host, self._port)
            mailserver.ehlo()
            if self._starttls:
                mailserver.starttls()
                if self._login is not None and self._password is not None:
                    mailserver.login(self._login, self._password)
            for mail in self._mails[group::ngroups]:
                mailserver.send_message(mail.to_email())
                time.sleep(wait)
            del mailserver
        self._mails.clear()

    def _show_mails_in_pager(self):
        pager = os.environ.get("PAGER", "less")
        sp = subprocess.Popen((pager,), stdin=subprocess.PIPE)

        mail_format = textwrap.dedent(
            """\
            #
            # Mail {i}
            #
            {mail}
        """
        )

        mails = "\n".join(
            mail_format.format(i=i, mail=mail) for i, mail in enumerate(self._mails)
        )
        sp.stdin.write(mails.encode())
        sp.communicate()

    def prompt(self, wait=0):
        while True:
            print(
                f"Loaded {len(self._mails)} mails. What do you want to do with?",
                file=sys.stderr,
            )
            print(f" - show", file=sys.stderr)
            print(f" - send", file=sys.stderr)
            print(f" - quit", file=sys.stderr)
            try:
                choice = input("Choice: ")
            except EOFError:
                choice = "quit"

            if choice == "quit":
                return None
            elif choice == "send":
                validation = "I want send {number} mails."
                print(
                    f'To confirme, type "{validation.format(number="<number>")}"',
                    file=sys.stderr,
                )
                sentence = input("Confirmation: ")
                if sentence == validation.format(number=len(self._mails)):
                    self.send_mails(wait)
                    print("Done", file=sys.stderr)
                    return None
                print("Not confirmed", file=sys.stderr)
                continue
            elif choice == "show":
                try:
                    self._show_mails_in_pager()
                except BrokenPipeError:
                    pass
                continue
            print(f"Incorrect input.\n", file=sys.stderr)
