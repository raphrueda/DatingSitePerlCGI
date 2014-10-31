##COMP2041 Assignment 2

A dating site for university students

##Matching Algorithm

A total of 80 points can be aquired from bio information, i.e. age, hair colour, weight and height (20 each).

For age, 20 points is awarded if the candidate's age falls in the user's preferred range. From then on there is a 3 point deduction for every year out of the range.

For hair colour, 20 points is awarded if candidate matches one of the user's preferred colours. 0 otherwise.

For height, 20 points is awarded if the candidate's height falls in the user's preffered range. From then on there is a 1 point deduction for every cm out of range.

For weight, 20 points is awarded if the candidate's weight falls in the user's preffered range. From then on there is a 2 point deduction for every kg out of range.

In the case where the user does not specify a preference for any of the above, it is assumed they do not care and the candidate receives 20 points.

However for age, if min/max is not specified, then min and max take the following formulas: (age/2)+7 and (age-7)*2.

Bonus points are rewarded for each common interest as follows:
    - Book: 3 point(s)
    - Movie: 3 point(s)
    - TV Show: 3 point(s)
    - Hobby: 5 point(s)
    - Course: 1 point(s)

Any candidate that meets a compatibility score of 60+ points is recommended as a possible match.
