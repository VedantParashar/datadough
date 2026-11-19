# Design decisions

The ten decisions that shape Datadough's numbers most, and why I made them. The full rules, with more
examples, are in [METHODOLOGY.md](METHODOLOGY.md).

## 1. The latest filing wins

The same fiscal year appears in up to three annual reports, and the later ones sometimes restate it. I
use the value from the most recently filed report, because a restatement is the company correcting
itself. Apple's FY2008 revenue was first filed as $32,479M and later restated to $37,491M; the app shows
$37,491M.

## 2. A split needs two signs, not one

Old per-share figures have to be put on today's share basis. I treat a change as a stock split only when
a later filing reports an earlier year's EPS at a clean ratio (2-for-1, 10-for-1, 3-for-2…) **and** that
year's net income is unchanged within 1%. The second test is what tells a split from a restatement. NVIDIA's
4-for-1 (2021) and 10-for-1 (2024) splits are caught; Apple's FY2008 EPS change isn't, because its net
income moved too.

## 3. Two kinds of equity

Total equity includes minority owners, so I use it for the balance check (assets = liabilities +
equity). Ratios like ROE use shareholders' equity, the parent company's share, because net income is the
parent's profit too. When a company only tags total equity, I subtract minority interest and label the
result as calculated.

## 4. Leaving Tesla's FY2014–15 balance check failing

Tesla's balance sheet doesn't add up in the data for FY2014 and FY2015, by $58M and $47M: the equity part
of its convertible notes. The only tag holding that amount means something different at other
companies, and adding it would have broken NVIDIA's check in 4 of its 18 years. I left the two years
failing, because a failed check is the honest result ([#3](https://github.com/VedantParashar/finance-analyzer/issues/3)).

## 5. Total revenues first

Some companies tag both total revenues and revenue from contracts with customers. I take total revenues,
because the contract figure can leave real revenue out: Walmart's membership income, or most of
American Tower's rent ($10,645M total against $936M). The cost is that a "total" which also holds other
income counts it too, as with Chevron ([#75](https://github.com/VedantParashar/finance-analyzer/issues/75)).

## 6. TSMC's bonds and Novo Nordisk's bonds

TSMC reports TWD 926.6bn of bonds on a separate line from TWD 31.8bn of borrowings, so counting
borrowings only made its debt/equity 0.02× instead of 0.24×. Novo Nordisk tags its DKK 111.4bn of bonds
*inside* its DKK 118.9bn of borrowings, so adding them would nearly double its debt. My rule: add bonds
only when they're larger than the borrowings figure, since a part can't be bigger than its whole.

## 7. Share counts filed in thousands: the EPS test

Some filings give diluted shares in thousands by mistake. EPS = net income ÷ diluted shares, so the same
year's net income and EPS say what the count must be. I multiply a count by 1,000 only when it doesn't
give the filed EPS and 1,000 times it does. That fixed NVIDIA FY2008–09, Advance Auto Parts FY2008
and Crocs FY2012 without guessing.

## 8. Absent is not zero

A missing value stays missing, and the metric says why. Apple stopped reporting interest expense after
FY2023, so its interest coverage reads "unavailable", not infinite. Only a short list of items many
companies simply don't have (inventory, debt, short-term investments) counts as 0, and only if the
company has never reported it in any year, with a note saying so.

## 9. Altman Z″, not the classic Z

The classic Altman Z needs the market value of equity, and the app only knows today's share price, so it
couldn't give a score for each past year. I use Z″, Altman's 1995 version, which uses balance-sheet
equity instead and has its own cut-offs (2.6 and 1.1). Its numbers won't match sites that show the
classic score, so the card is labelled "Altman Z″".

## 10. Calculate only what holds by definition

When a line item isn't tagged, I calculate it only by a rule that's true by definition, like Coca-Cola's
total liabilities = total liabilities and equity − total equity ($70,541M in FY2025). Every calculated
value is marked and shows its formula. I never fill a gap with an estimate.
