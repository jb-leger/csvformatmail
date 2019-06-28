# csvformatmail: A tool to manipulate csv file with headers

## Installing

From pypi (not yet on pypi):

```
pip3 install csvformatmail
```

Or developer version:

```
git clone <this repo>
cd csvformatmail
pip3 install -e .
```

## Enable completion (for bash or other shells using bash-completion)

```
mkdir -p ~/.local/share/bash-completion/completions
register-python-argcomplete csvformatmail > ~/.local/share/bash-completion/completions/csvformatmail
```

## Python module

All methods and functions are accessible in the python module.

## Example

Write a mail template:

```
From: My name <my-mail-address@example.org>
To: {mail}
Subject: Result of the last test

Dear {firstname} {lastname.capitalize()},

Your results of the last test are:

 - Part A: {a:.1f}
 - Part B: {b:.1f}

Therefore you {"pass" if a+b>50 else "fail"} the test.

-- 
signature
```

Use a csv file with (at least) the columns `firstname`, `lastname`, `mail`, `a`
and `b`:

```
firstname,lastname,mail,a,b,c
Jacques,MARTIN,jacques.martin@example.org,12.54441,14,1111.221
…
```

And the command:

```
csvformatmail template.txt -t a:float -b:float listing.csv
```
