# Synthetic Case Data

`cases.csv` contains the initial 40 labeled synthetic invoice/payment cases.

CSV is the canonical dataset because the case schema is flat and easy to inspect
in a spreadsheet. The loader converts CSV text back into validated Python
types before the agent uses the cases.

The cases are generated with seed `42` and are not real-world incidents. The
`true_state` field is available to the evaluator after prediction but must not
be passed to the agent as input. Use `InvoiceCase.observation()` for the
prediction-time view.

Initial distribution:

| Hidden state | Cases |
|---|---:|
| `LEGITIMATE` | 16 |
| `ERROR` | 12 |
| `FRAUD` | 12 |
| Total | 40 |
