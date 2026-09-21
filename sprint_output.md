#Sprint Output

## Feature: help me to write a python function for finding factorial of a number
**Phase:** SprintPhase.DONE
**Turns:** 1
**Tests Passed:** False
## Conversation Log

### Turn 1 - Product Manager

**Requirements for the Factorial Function**

The following requirements are for the `factorial` function:

1. **Input Validation**: The function should accept a non-negative integer as input.
2. **Base Case**: The function should handle the case where the input number is 0 or 1, as these are the base cases for factorial.
3. **Recursive Case**: The function should calculate the factorial of a number by recursively multiplying all integers from 2 to the input number.
4. **Integer Overflow**: The function should handle the case where the input number is larger than the maximum integer that can be represented by a 32-bit or 64-bit signed integer.
5. **Error Handling**: The function should handle any errors that may occur during execution, such as division by zero or invalid input.

**Example Use Cases**

* `factorial(5)` should return `120`.
* `factorial(0)` should return `1`.
* `factorial(-1)` should raise an error (or handle it in a way that makes sense for the specific use case).
* `factorial(1e308)` should raise an error (or handle it in a way that makes sense for the specific use case).

**Code Requirements**

* The function should be written in Python 3.x.
* The function should use recursive function calls to calculate the factorial.
* The function should use integer arithmetic to avoid overflow errors.
* The function should handle any potential errors that may occur during execution.

TERMINATE
