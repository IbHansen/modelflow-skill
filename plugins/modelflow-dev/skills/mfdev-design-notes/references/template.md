# <Title>

Design note for `<module>.py`. <One line: what is added or changed.>
Hand to Claude Code for implementation. No code has been written yet.

## 1. Idea

<Two to five sentences: the problem and the idea that solves it.>

## 2. What the code looks like today (findings)

- <function / class>: <what it does now, with the relevant names and signatures>
- <...>

### Measured potential

<How the gain was estimated (probe, timing), the numbers, the realistic ceiling.
Leave out if the change is not about performance.>

## 3. Rule

<The precise rule the implementation follows: invariance rule, syntax, data layout,
selection criteria. A table when there are cases.>

## 4. Design

### 4.1 <Storage / data>
### 4.2 <Code generation / parsing>
### 4.3 <New flavours, options or classes>
### 4.4 <Changes to existing classes - each listed, each minimal>
### 4.5 <Diagnostics>
### 4.6 <Debug / error location>

## 5. Numerical equivalence

- Non-jit: <bit-identical to ...> - the primary regression test.
- Jit: <tolerance and why>.

## 6. Out of scope / later

- <...>

## 7. Phases

1. <testable step>
2. <...>

## 8. Decisions

1. <decision as the user stated it>
