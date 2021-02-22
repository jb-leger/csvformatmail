# csvformatmail: A tool to format mails from csv and to send them

## Installing

From pypi:

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

And the command if you have a local smtp:

```
csvformatmail template.txt -t a:float -t b:float listing.csv
```

Or if you use a distant smtp:

```
csvformatmail -h smtp.example.org -l mylogin template.txt -t a:float -t b:float listing.csv
```

## Complex example

The template file can contain python definition, and all the column is
accessible by the names `cols` (default name, can be changed with arg
`--colsname`). See the following template file:

```
# python preamble begin
import numpy as np
def quartiles(list_values):
    q1, q2, q3 = np.percentile(list_values, (25,50,75))
    return f"{q1:.1f}, {q2:.1f}, {q3:.1f}"
# python preamble end

From: My name <my-mail-address@example.org>
To: {mail}
Subject: Result of the last test

Dear {firstname} {lastname.capitalize()},

Your results of the last test are:

 - Part A: {a:.1f}
 - Part B: {b:.1f}

For all the class, the mean of part A is {np.mean(cols['a']):.1}, and the
quartiles are {quartiles(cols['a'])}.

Therefore you {"pass" if a+b>50 else "fail"} the test.

-- 
signature
```

## Misc

Consider use function `fill` and `indent` of `textwrap` module. For this you
need use `-b "import textwrap"` or add a python preamble in you template file.
_e.g._ in a template to rewrap to 72 chars:

```
{textwrap.fill(somevalue, width=72)}
```

Or, for rewrap and indent by `> `:

```
{textwrap.indent(textwrap.fill(somevalue, width=70), "> ")}
```
