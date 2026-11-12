# Shared Expense CSV Splitter

A small, dependency-free command-line utility for allocating itemized receipt amounts across named participants. It reads a CSV, splits each line in integer cents, and assigns any leftover cents by largest remainder. Ties follow the participant order in the input file.

## What it does

- Accepts item descriptions, amounts, and the participants sharing each line.
- Keeps all calculations in integer cents to avoid floating-point currency errors.
- Writes one allocation row per item and a per-person total.
- Makes the remainder rule explicit and reproducible.

This is a transparent example of a receipt-allocation method, not tax, accounting, or reimbursement advice. It does not infer who owes whom, apply tax or tip rules, or claim that its allocation is an industry standard. Check the source receipt and agree on the sharing rules before using the output.

## Requirements

Python 3.10 or newer. No third-party packages are required.

## Input CSV

Use these columns:

| Column | Meaning | Example |
| --- | --- | --- |
| `item` | Line description | `Shared appetizer` |
| `amount` | Non-negative amount with at most two decimal places | `10.00` |
| `participants` | Names sharing the line, separated by `|` | `Alex|Jordan|Sam` |

The participant names are case-sensitive. A person is counted once per line even if repeated in that line.

## Run

```console
python split_receipt.py example.csv --allocations allocations.csv --totals totals.csv
```

The sample file is synthetic and is provided only to demonstrate the input format. Replace it with values you have permission to use.

## Allocation rule

Each line is converted to integer cents. Every listed participant first receives the floor of an equal share. Remaining cents are assigned to participants with the largest fractional remainders; ties are resolved in the order the names appear in that line. Therefore, each line's allocated cents always sum to that line's input cents.

## Related resource

For more shared-expense tools and printable worksheets, visit [The Even Table](https://theeventable.com/).

For a browser-based version, see [The Even Table receipt splitter](https://theeventable.com/receipt-splitter/).

## License

MIT. See [LICENSE](LICENSE).
