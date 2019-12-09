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
    def __init__(self, host="localhost", port=25):
        self._mailserver = smtplib.SMTP(host, port)
        self._mails = []

    def add_mail(self, mail):
        self._mails.append(mail)

    def send_mails(self, wait=0):
        for mail in self._mails:
            self._mailserver.send_message(mail.to_email())
            time.sleep(wait)
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

    def prompt(self):
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
                    self.send_mails()
                    print("Done", file=sys.stderr)
                    return None
                print("Not confirmed", file=sys.stderr)
                continue
            elif choice == "show":
                self._show_mails_in_pager()
                continue
            print(f"Incorrect input.\n", file=sys.stderr)
