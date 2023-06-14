EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr User 5709 4134
encoding utf-8
Sheet 17 37
Title "Quantum Random Number Generator"
Date "2021-09-27"
Rev "v2.1"
Comp "University of California, Santa Barbara"
Comment1 "Biomimetic Circuits and Nanosystems Group"
Comment2 "Zachary Nelson"
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 2000 750  2    50   Input ~ 0
3.3V
Text GLabel 1300 1200 2    50   Input ~ 0
GND
Text GLabel 3450 1350 2    50   Input ~ 0
HV
$Comp
L power:PWR_FLAG #FLG01
U 1 1 611EE70A
P 1900 750
F 0 "#FLG01" H 1900 825 50  0001 C CNN
F 1 "PWR_FLAG" H 1900 923 50  0000 C CNN
F 2 "" H 1900 750 50  0001 C CNN
F 3 "~" H 1900 750 50  0001 C CNN
	1    1900 750 
	1    0    0    -1  
$EndComp
$Comp
L power:PWR_FLAG #FLG02
U 1 1 611EE95A
P 1200 1200
F 0 "#FLG02" H 1200 1275 50  0001 C CNN
F 1 "PWR_FLAG" H 1200 1373 50  0000 C CNN
F 2 "" H 1200 1200 50  0001 C CNN
F 3 "~" H 1200 1200 50  0001 C CNN
	1    1200 1200
	-1   0    0    1   
$EndComp
Wire Wire Line
	1200 1200 1300 1200
Wire Wire Line
	1900 750  2000 750 
$Comp
L Custom_Part_Library:NCP187 U31
U 1 1 6121FAC8
P 1500 900
F 0 "U31" H 1500 1227 50  0000 C CNN
F 1 "NCP187" H 1500 1155 26  0000 C CNN
F 2 "Custom_Footprint_Library:WDFN-6-1EP_2x2mm_P0.65mm_EP1.12x1.72" H 1500 1000 50  0001 C CNN
F 3 "" H 1500 1000 50  0001 C CNN
	1    1500 900 
	1    0    0    -1  
$EndComp
Wire Wire Line
	1200 750  1100 750 
Wire Wire Line
	1100 750  1100 900 
Wire Wire Line
	1100 900  1200 900 
Wire Wire Line
	1800 750  1900 750 
Wire Wire Line
	1900 750  1900 900 
Wire Wire Line
	1900 900  1800 900 
Connection ~ 1900 750 
Wire Wire Line
	1200 1200 1200 1050
Connection ~ 1200 1200
Wire Wire Line
	1100 750  1000 750 
Connection ~ 1100 750 
Text GLabel 1000 750  0    50   Input ~ 0
IN_PWR
$Comp
L Device:R_US R76
U 1 1 61223784
P 2000 1050
F 0 "R76" H 2068 1096 50  0000 L CNN
F 1 "10K" H 2068 1005 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 2040 1040 50  0001 C CNN
F 3 "~" H 2000 1050 50  0001 C CNN
	1    2000 1050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1800 1050 1800 1200
Wire Wire Line
	1800 1200 2000 1200
Wire Wire Line
	2000 900  1900 900 
Connection ~ 1900 900 
Text GLabel 2800 750  0    50   Input ~ 0
IN_PWR
Text GLabel 3300 750  2    50   Input ~ 0
3.3V
Text GLabel 3050 1050 3    50   Input ~ 0
GND
$Comp
L Device:C C106
U 1 1 61224C0E
P 2900 900
F 0 "C106" H 3015 946 50  0000 L CNN
F 1 "1u" H 3015 855 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 2938 750 50  0001 C CNN
F 3 "~" H 2900 900 50  0001 C CNN
	1    2900 900 
	1    0    0    -1  
$EndComp
$Comp
L Device:C C107
U 1 1 612254CE
P 3200 900
F 0 "C107" H 3315 946 50  0000 L CNN
F 1 "10u" H 3315 855 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 3238 750 50  0001 C CNN
F 3 "~" H 3200 900 50  0001 C CNN
	1    3200 900 
	1    0    0    -1  
$EndComp
Wire Wire Line
	2900 1050 3200 1050
Wire Wire Line
	3200 750  3300 750 
Wire Wire Line
	2800 750  2900 750 
$Comp
L Custom_Part_Library:BANANA B1
U 1 1 6122A2AC
P 3950 1800
F 0 "B1" H 3808 2065 50  0000 C CNN
F 1 "BANANA" H 3808 1974 50  0000 C CNN
F 2 "Custom_Footprint_Library:CT3151-Horizontal" H 3950 2000 50  0001 C CNN
F 3 "" H 3950 2000 50  0001 C CNN
	1    3950 1800
	1    0    0    -1  
$EndComp
$Comp
L Custom_Part_Library:BANANA B2
U 1 1 6122A903
P 4800 1800
F 0 "B2" H 4658 2065 50  0000 C CNN
F 1 "BANANA" H 4658 1974 50  0000 C CNN
F 2 "Custom_Footprint_Library:CT3151-Horizontal" H 4800 2000 50  0001 C CNN
F 3 "" H 4800 2000 50  0001 C CNN
	1    4800 1800
	1    0    0    -1  
$EndComp
$Comp
L Custom_Part_Library:BANANA B3
U 1 1 6122B6DB
P 4800 2250
F 0 "B3" H 4658 2515 50  0000 C CNN
F 1 "BANANA" H 4658 2424 50  0000 C CNN
F 2 "Custom_Footprint_Library:CT3151-Horizontal" H 4800 2450 50  0001 C CNN
F 3 "" H 4800 2450 50  0001 C CNN
	1    4800 2250
	1    0    0    -1  
$EndComp
Text GLabel 4900 1800 2    50   Input ~ 0
IN_PWR
Text GLabel 4900 2250 2    50   Input ~ 0
GND
Text GLabel 4300 1100 0    50   Input ~ 0
HV
Text GLabel 4300 1400 0    50   Input ~ 0
GND
$Comp
L Device:C C138
U 1 1 611585EC
P 4600 1250
F 0 "C138" H 4715 1296 50  0000 L CNN
F 1 "1u" H 4715 1205 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4638 1100 50  0001 C CNN
F 3 "~" H 4600 1250 50  0001 C CNN
	1    4600 1250
	1    0    0    -1  
$EndComp
$Comp
L Device:C C139
U 1 1 6115867E
P 4900 1250
F 0 "C139" H 5015 1296 50  0000 L CNN
F 1 "10u" H 5015 1205 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4938 1100 50  0001 C CNN
F 3 "~" H 4900 1250 50  0001 C CNN
	1    4900 1250
	1    0    0    -1  
$EndComp
$Comp
L Device:C C137
U 1 1 6115E553
P 4300 1250
F 0 "C137" H 4415 1296 50  0000 L CNN
F 1 "1n" H 4415 1205 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4338 1100 50  0001 C CNN
F 3 "~" H 4300 1250 50  0001 C CNN
	1    4300 1250
	1    0    0    -1  
$EndComp
Wire Wire Line
	4300 1100 4600 1100
Connection ~ 4600 1100
Wire Wire Line
	4600 1100 4900 1100
Wire Wire Line
	4300 1400 4600 1400
Connection ~ 4600 1400
Wire Wire Line
	4600 1400 4900 1400
Text GLabel 4300 600  0    50   Input ~ 0
HV
Text GLabel 4300 900  0    50   Input ~ 0
GND
$Comp
L Device:C C141
U 1 1 61168276
P 4600 750
F 0 "C141" H 4715 796 50  0000 L CNN
F 1 "1u" H 4715 705 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4638 600 50  0001 C CNN
F 3 "~" H 4600 750 50  0001 C CNN
	1    4600 750 
	1    0    0    -1  
$EndComp
$Comp
L Device:C C142
U 1 1 61168280
P 4900 750
F 0 "C142" H 5015 796 50  0000 L CNN
F 1 "10u" H 5015 705 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4938 600 50  0001 C CNN
F 3 "~" H 4900 750 50  0001 C CNN
	1    4900 750 
	1    0    0    -1  
$EndComp
$Comp
L Device:C C140
U 1 1 6116828A
P 4300 750
F 0 "C140" H 4415 796 50  0000 L CNN
F 1 "1n" H 4415 705 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4338 600 50  0001 C CNN
F 3 "~" H 4300 750 50  0001 C CNN
	1    4300 750 
	1    0    0    -1  
$EndComp
Wire Wire Line
	4300 600  4600 600 
Connection ~ 4600 600 
Wire Wire Line
	4600 600  4900 600 
Wire Wire Line
	4300 900  4600 900 
Connection ~ 4600 900 
Wire Wire Line
	4600 900  4900 900 
Text GLabel 4050 1800 2    50   Input ~ 0
IN_HV
Wire Wire Line
	1900 1750 2000 1750
Text GLabel 1050 1950 3    50   Input ~ 0
GND
$Comp
L power:PWR_FLAG #FLG0101
U 1 1 616250A7
P 2000 1750
F 0 "#FLG0101" H 2000 1825 50  0001 C CNN
F 1 "PWR_FLAG" H 2000 1923 50  0000 C CNN
F 2 "" H 2000 1750 50  0001 C CNN
F 3 "~" H 2000 1750 50  0001 C CNN
	1    2000 1750
	1    0    0    -1  
$EndComp
Connection ~ 2000 1750
Wire Wire Line
	2000 1750 2400 1750
Text GLabel 750  1750 0    50   Input ~ 0
IN_HV
Wire Wire Line
	1050 1950 1200 1950
$Comp
L Device:R_US R77
U 1 1 61628B78
P 1950 2150
F 0 "R77" H 2018 2196 50  0000 L CNN
F 1 "959" H 2018 2105 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 1990 2140 50  0001 C CNN
F 3 "~" H 1950 2150 50  0001 C CNN
	1    1950 2150
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R78
U 1 1 6162940C
P 2300 2000
F 0 "R78" V 2095 2000 50  0000 C CNN
F 1 "15k" V 2186 2000 50  0000 C CNN
F 2 "Resistor_SMD:R_0603_1608Metric" V 2340 1990 50  0001 C CNN
F 3 "~" H 2300 2000 50  0001 C CNN
	1    2300 2000
	0    1    1    0   
$EndComp
$Comp
L Device:R_POT_US RV3
U 1 1 61629F03
P 2700 2000
F 0 "RV3" V 2587 2000 50  0000 C CNN
F 1 "15k" V 2496 2000 50  0000 C CNN
F 2 "Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical" H 2700 2000 50  0001 C CNN
F 3 "~" H 2700 2000 50  0001 C CNN
	1    2700 2000
	0    -1   -1   0   
$EndComp
Wire Wire Line
	1900 1850 1950 1850
Wire Wire Line
	1950 1850 1950 2000
Wire Wire Line
	2150 2000 1950 2000
Connection ~ 1950 2000
Wire Wire Line
	2700 1850 2400 1850
Wire Wire Line
	2400 1850 2400 1750
Connection ~ 2400 1750
Wire Wire Line
	2450 2000 2550 2000
Text GLabel 1950 2350 0    50   Input ~ 0
GND
Wire Wire Line
	1950 2300 1950 2350
Wire Wire Line
	750  1750 850  1750
$Comp
L Device:C C143
U 1 1 61636A58
P 850 1900
F 0 "C143" H 965 1946 50  0000 L CNN
F 1 "1u" H 965 1855 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 888 1750 50  0001 C CNN
F 3 "~" H 850 1900 50  0001 C CNN
	1    850  1900
	1    0    0    -1  
$EndComp
Connection ~ 850  1750
Wire Wire Line
	850  2050 850  2150
Text GLabel 850  2150 3    50   Input ~ 0
GND
$Comp
L Device:C C144
U 1 1 61638DE5
P 2400 1600
F 0 "C144" H 2515 1646 50  0000 L CNN
F 1 "3.3u" H 2515 1555 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 2438 1450 50  0001 C CNN
F 3 "~" H 2400 1600 50  0001 C CNN
	1    2400 1600
	1    0    0    -1  
$EndComp
Text GLabel 2400 1400 2    50   Input ~ 0
GND
Wire Wire Line
	2400 1450 2400 1400
$Comp
L Custom_Part_Library:PinHeader_1x2 J4
U 1 1 61579848
P 3050 1950
F 0 "J4" V 2946 2088 50  0000 L CNN
F 1 "PinHeader_1x2" V 3037 2088 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 3200 2300 50  0001 C CNN
F 3 "" H 3050 2500 50  0001 C CNN
	1    3050 1950
	0    1    1    0   
$EndComp
$Comp
L Custom_Part_Library:PinHeader_1x2 J3
U 1 1 61579F9B
P 3050 1550
F 0 "J3" V 2946 1688 50  0000 L CNN
F 1 "PinHeader_1x2" V 3037 1688 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 3200 1900 50  0001 C CNN
F 3 "" H 3050 2100 50  0001 C CNN
	1    3050 1550
	0    1    1    0   
$EndComp
Wire Wire Line
	3100 1350 3300 1350
Wire Wire Line
	3100 1750 3300 1750
Wire Wire Line
	3300 1750 3300 1350
Connection ~ 3300 1350
Wire Wire Line
	3300 1350 3450 1350
Wire Wire Line
	2400 1750 3000 1750
Text GLabel 2900 1350 0    50   Input ~ 0
IN_HV
Wire Wire Line
	2900 1350 3000 1350
Wire Wire Line
	850  1750 1100 1750
Wire Wire Line
	1200 1850 1100 1850
Wire Wire Line
	1100 1850 1100 1750
Connection ~ 1100 1750
Wire Wire Line
	1100 1750 1200 1750
$Comp
L Custom_Part_Library:LT3012 U36
U 1 1 6158F3B7
P 1550 1850
F 0 "U36" H 1550 2265 50  0000 C CNN
F 1 "LT3012" H 1550 2174 50  0000 C CNN
F 2 "Package_SO:TSSOP-16-1EP_4.4x5mm_P0.65mm" H 1350 2150 50  0001 C CNN
F 3 "" H 1350 2150 50  0001 C CNN
	1    1550 1850
	1    0    0    -1  
$EndComp
$EndSCHEMATC
