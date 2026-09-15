=========================
 TUP Solution Validator
=========================

Java 1.8 is required to run the Traveling Umpire Problem (TUP) solution validator.

Usage: java -jar validator.jar <instance> <q1> <q2> <solution>
    <instance> : Instance name (example: umps14).
    <q1>       : Value for parameter q1 (example: 7).
    <q2>       : Value for parameter q2 (example: 3).
    <solution> : Solution file (example: umps14_7_3.txt).

Example:
    java -jar validator.jar umps14.txt 7 3 umps14_7_3.txt

In case of success, the validator will print the solution cost. Otherwise, it will either print an error message or the message "Solution is infeasible!".

If you have any questions, please contact:
    - tony.wauters@kuleuven.be
