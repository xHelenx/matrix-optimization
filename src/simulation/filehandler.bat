echo "%1" "%2" "%3">erg.txt
copy %1%2.temp %1%2.xml
*: copy E:\Bachelorarbeit\src\simulation\%1.temp E:\Bachelorarbeit\src\simulation\tmp\%2_%1.txt
del %1%2.temp