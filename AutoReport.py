# Fully Automatic Python Code for report generation
# By Abhinav Anand
import sys
import glob
import os # for automatic opening of file
import pandas as pd
import numpy as np
import http.server
import socketserver

pd.options.mode.chained_assignment = None
PORT = 9997

handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print("Server started at localhost:" + str(PORT))
    


    fi=[]
    for file_name in glob.iglob('*.txt', recursive=True): # to find the required file without hardcoding
        fi.append(file_name)
    li = []
    with open(fi[0],'rt') as f:
        for line in f:
            inner_list = [line.strip() for line in line.split('split character')]
            li.append(inner_list) # contents of the file are split into a list


    # For filling up left out entries for uniformity
    for i in range(6,len(li),7):
        if(li[i] != ['']):
            li.insert(i-3,[''])
    flatList = [ item for elem in li for item in elem]

    # To split the list into 7 equal parts based on the requirement
    f=[]
    for i in range(0,len(li),7):
        x=i
        f.append(flatList[x:x+7])
    data=pd.read_csv(fi[1],names=['FileName'])
    df = pd.DataFrame(f,columns=['FileName','Lines','Branches','Taken_at_least','Calls','Creating','Gap'])# Naming in columns 
    finaldf=df[['Lines','Branches','Taken_at_least','Calls']]
    finaldf['Branches']=finaldf['Branches'].str.replace("Branches executed:",'')
    finaldf['Branches']=finaldf['Branches'].str.replace("No branches",'nan')
    finaldf['Lines']=finaldf['Lines'].str.replace("Lines executed:",'')
    finaldf['Calls']=finaldf['Calls'].str.replace("No calls",'nan')
    finaldf['Calls']=finaldf['Calls'].str.replace("Calls executed:",'')
    finaldf['Taken_at_least']=finaldf['Taken_at_least'].str.replace("Taken at least once:",'')
    df2=pd.concat([data, finaldf.reindex(data.index)], axis=1)
    df2['Line_Total']=''
    df2['Branches_Total']=''
    df4 = pd.DataFrame()
    for i in range(0,len(df2)):
        if(len(df2['Branches'][i].split("%", 1))==2):
            df2['Branches_Total'][i]=(df2['Branches'][i].split("%", 1)[1])
        df2['Line_Total'][i]= df2['Lines'][i].split("%", 1)[1]
        df2['Lines'][i] = df2['Lines'][i].split("%", 1)[0]
        
        df2['Branches'][i] = df2['Branches'][i].split("%", 1)[0]
        df2['Calls'][i] = df2['Calls'][i].split("%", 1)[0]
        df2['Taken_at_least'][i] = df2['Taken_at_least'][i].split("%", 1)[0]
    df2['Branches_Total']=df2['Branches_Total'].str.replace('[^0-9]', '',regex=True)
    df2['Line_Total']=df2['Line_Total'].str.replace('[^0-9]', '',regex=True)

        
        
    def color(value): # to provide color based on the severity
        if(type(value) != str):
            if (value < 75.00 and value >=+0.00):
                color = 'red'
            elif (value >= 75.00 and value <=90):
                color = 'yellow'
            elif value >= 90.00:
                color = 'green' 
        else:
            color = 'grey'

        return 'background-color: %s' % color
    # the contenets are converted to float for comparison
    df2['Lines']=df2['Lines'].astype(float) 
    df2['Branches']=df2['Branches'].astype(float)
    df2['Calls']=df2['Calls'].astype(float)
    df2=df2.replace(r'^\s*$', np.nan, regex=True)
    lal=[]
    loc = os.getcwd()
    for i in df2['FileName']:
        loc=loc.replace("C:\\Users\\abhin\\","")
        lal.append("http://localhost:9997\\"+"\\"+i)
    df2['FileLocation']=lal

    df2= df2[['FileName','Lines','Line_Total','Branches','Branches_Total','Taken_at_least','Calls','FileLocation']]

    df2=df2.style.applymap(color, subset=['Lines','Branches']).set_properties(**{'text-align': 'center'}).set_table_styles([ dict(selector='th', props=[('text-align', 'left')] )])

    df2.data=df2.data.fillna('-%')
    #print(df2.data)
    def func(row):
        xml = ['<item>']
        for field in row.index:
            xml.append('  <{0}>{1}</{0}>'.format(field, row[field]))
        xml.append('</item>')
        return '\n'.join(xml)
    original_stdout = sys.stdout
    print("Your Report is ready! All files can be found in the file folder")
    with open('xmlfile.xml', 'w') as f:
        sys.stdout = f 
        print('<?xml version="1.0" encoding="UTF-8"?>')
        print('<list>') # To give the parent tag
        print ('\n'.join(df2.data.apply(func, axis=1)))
        print('</list>') # ending the parent tag


    f= open("table.html","w+") # to write a new HTML page table

    f.write('''<!DOCTYPE html>
    <html lang="en">

    <head>
            <meta charset="UTF-8">
            <title>GCC Report Response Table </title>
            <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
            <script>
                    window.addEventListener("load", function () {
                            getRows();
                    });
                    
                    
                    function getRows() {
                            var xmlhttp = new XMLHttpRequest();
                            xmlhttp.open("get", "xmlfile.xml", true); // to read data from the XML file
                            xmlhttp.onreadystatechange = function () {
                                    if (this.readyState == 4 && this.status == 200) {
                                            showResult(this);
                                    }
                            };
                            xmlhttp.send(null);
                    }

                    function showResult(xmlhttp) {
                            var xmlDoc = xmlhttp.responseXML.documentElement;
                            removeWhitespace(xmlDoc);
                            var outputResult = document.getElementById("BodyRows");
                            var rowData = xmlDoc.getElementsByTagName("item");
                            addTableRowsFromXmlDoc(rowData, outputResult);
                            colorCells();
                            total();
                            filelinks();
                            console.log("cell: " + document.getElementsByTagName("td").length);
                    }
                    

                    function addTableRowsFromXmlDoc(xmlNodes, tableNode) { // to bring XML data into tabulated form in HTML
                            var theTable = tableNode.parentNode;
                            var newRow, newCell, i;
                            console.log("Number of nodes: " + xmlNodes.length);
                            
                            for (i = 0; i < xmlNodes.length; i++) {
                                    newRow = tableNode.insertRow(i);

                                    for (j = 0; j < xmlNodes[i].childNodes.length; j++) {
                                            newCell = newRow.insertCell(newRow.cells.length);
                                            if (xmlNodes[i].childNodes[j].firstChild) {
                                                    newCell.innerHTML = xmlNodes[i].childNodes[j].firstChild.nodeValue;
                                            }
                                            
                                    }
                                    
                            }
                            
                            theTable.appendChild(tableNode);
                    }

                    function removeWhitespace(xml) { // removing unwanted whitespaces while bring XML to table
                            var loopIndex;
                            for (loopIndex = 0; loopIndex < xml.childNodes.length; loopIndex++) {
                                    var currentNode = xml.childNodes[loopIndex];
                                    if (currentNode.nodeType == 1) {
                                            removeWhitespace(currentNode);
                                    }
                                    if (!(/\S/.test(currentNode.nodeValue)) && (currentNode.nodeType == 3)) {
                                            xml.removeChild(xml.childNodes[loopIndex--]);
                                    }
                            }
                    }
                    function colorCells() { // condition for coloring based on the severity
                            var y = document.getElementsByTagName("td");
                            for (i = 1; i < y.length; i = i + 8) {
                                    if (y[i].innerHTML > 89) {
                                             y[i].style.backgroundColor = "green"; 
                                             y[i + 1].style.backgroundColor = " green" ;
                                    }
                                    if (y[i].innerHTML < 75) {
                                             y[i].style.backgroundColor = "red"; 
                                             y[i + 1].style.backgroundColor = " red" ;
                                    }
                                    if (y[i].innerHTML > 75 & y[i].innerHTML < 90) {
                                             y[i].style.backgroundColor = "yellow"; 
                                            y[i + 1].style.backgroundColor = " yellow" ;

                                            
                                    }
                                    
                                    
                            }
                            for (j = 3; j < y.length; j = j + 8) {
                                    if (y[j].innerHTML > 89) {
                                             y[j].style.backgroundColor = "green"; 
                                             y[j + 1].style.backgroundColor = " green" ;
                                    }
                                    if (y[j].innerHTML > 75 & y[j].innerHTML < 90) {
                                             y[j].style.backgroundColor = "yellow"; 
                                             y[j + 1].style.backgroundColor = " yellow";

                                    }
                                    if (y[j].innerHTML < 75) {
                                             y[j].style.backgroundColor = "red"; 
                                             y[j + 1].style.backgroundColor = " red";
                                    }
                                    if (y[j].innerHTML == '-%') {
                                             y[j].style.backgroundColor = "grey"; 
                                             y[j + 1].style.backgroundColor = " grey";
                                    }
                                    //document.write(typeof y[3].innerHTML);
                            }


                    }
                    function filelinks() { 
                            var y = document.getElementsByTagName("td"); 
                            for (i = 0; i < y.length; i=i+8) {
                                    var result=(y[i].innerHTML).link(y[i+7].innerHTML);
                                    y[i].innerHTML = result;
                                    y[i+7].style.display = 'none';//removing address column
                            }
                            
                    }
                      function total() {  // get a sum of all lines and branches
                            var sum=0; 
                            var sum1=0;
                            var y = document.getElementsByTagName("td");
                            for (i = 2; i < y.length; i=i+8) {
                                    if (y[i].innerHTML > 0) {
                                            sum=sum+parseInt(y[i].innerHTML);					
                                    }			
                            }
                            for (i = 4; i < y.length; i = i + 8) {
                                    if (y[i].innerHTML > 0) {
                                            sum1=sum1+parseInt(y[i].innerHTML);					
                                    }			
                            }
                            
                            document.getElementById("LinesT").innerHTML ="Total number of Lines:  " + sum +" ";
                            document.getElementById("BranchT").innerHTML ="Total number of Branches:  " + sum1;
                            
                    }			
            </script>
            <style type="text/css">
                    h2 {
                            text-align: center;
                    }
                    p{
                            color:blue;
                    }

                    table,
                    th,
                    td {
                            border: 1px solid black;
                            border-collapse: collapse;
                    }

                    th,
                    td {
                            padding: 5px;
                    }

                    table.center {
                            margin-left: auto;
                            margin-right: auto;
                    }
            </style>
    </head>

    <body>
            <h2>GCC Code Coverage Report</h2>
            <!-- <hr color="blue">   -->
            <font color="white">
            <div style="width: 340px; height:20px;background-color: black;text-align: center;">Color Scheme</div></font>
            <div style="width: 110px; float:left; height:20px;background-color: green;">
                    High >= 90.0%
                    </div>
            
            <div style="width: 130px; float:left; height:20px;background-color: yellow">
                    Medium  >= 75.0%
                    </div>
                    <div style="width: 100px; float:left; height:20px;background-color: red;">
                    Low < 75.0%
                    </div>
            <div style="float:right;text-align:right;" id="LinesT"></div>
            <br>
            <div style="text-align:right;" id="BranchT"></div>
            
            
                    <table class="center" id="MainTable"> 
                    <tbody id="BodyRows"></tbody>
                    <tr style="background-color:DodgerBlue;">
                            
                            <th>FileName</th>
                            <th>Lines(in %)</th>
                            <th>Line_Total</th>
                            <th>Branches(in %)</th>
                            <th>Branches_Total</th>
                            <th>Taken_at_least(in %)</th>
                            <th>Calls(in %)</th>
                            
                            
                            
                    </tr>
            </table>
    </body>

    </html>''')
    f.close()
    
    # Chart HTML auto builing
    f= open("chart.html","w+") # to write a new HTML page 

    f.write('''<!DOCTYPE html>
    <html>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js"></script>
    <head><title>GCC Report Response Chart 1</title> <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <meta content="utf-8" http-equiv="encoding"></head>
    <center><p style="color:blueviolet;font-size:15px;">GCC Project Report</p> </center>
    <body>

    <canvas id="myChart" style="width:100%;max-width:1300px"></canvas>

    <script type="text/javascript" src="https://canvasjs.com/assets/script/jquery-1.11.1.min.js"></script>
    <script type="text/javascript" src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>

    <script type="text/javascript">
      
      window.onload = function() {
      var xe = [];
      var ye =[];
      var ze=[]
      $.get("xmlfile.xml", function(data) {
                    $(data).find("item").each(function () {
                            var $dataPoint = $(this);
                            var x = $dataPoint.find("FileName").text();
                            var y = $dataPoint.find("Lines").text();
          var z =  $dataPoint.find("Branches").text();
          
          ze.push(z);
          xe.push(x);
          ye.push(y);
                    });
    new Chart("myChart", {
     
      type: "horizontalBar",
      
      data: {
        labels: xe,
        datasets: [{
          label:"Lines",
          backgroundColor: "blue",
          data: ye
          },
      {
        label:"Branches",
        
        backgroundColor: "red",
        data: ze
      }]
      },
      
      options: {
        legend: {display: true},
        
        title: {
          //display: true,
          //text: "FileName Vs Quantity Executed"
        }
      }
    });
    })
    }

    </script>

    </body>
    </html>

    ''')
    f.close() 
    f= open("chart1.html","w+") # to write a new HTML page 

    f.write('''<!DOCTYPE HTML>
    <html>
    <head><title>GCC Report Response Chart 2</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <script type="text/javascript">
    window.onload = function() { 
     
    var data1 = [];
    var data2 = [];

    var chart = new CanvasJS.Chart("chartContainer", {
      animationEnabled: true,
            
            axisX:{
                    interval: 1,
        labelFontSize: 13,
        
            },
      
            // subtitles:[{
            // 	text: "GCC Chart"
            // }],
            data: [{
                    legendText: "Lines",
        axisYType: "secondary",
                    type: "stackedBar",
                    showInLegend: true, 
                    //indexLabel: "{y}",
                    //indexLabelPlacement: "inside",
                    dataPoints: data1,   
                    
            },{
        legendText: "Branches",
        axisYType: "secondary",
                    type: "stackedBar",
                    showInLegend: true, 
                    //indexLabel: "{y}",
                    //indexLabelPlacement: "inside",
                    dataPoints: data2,


      }]
    });
     
    $.get("xmlfile.xml", function (data) {
            $(data).find("item").each(function () {
                    var $dataPoint = jQuery(this);
                    var label = $dataPoint.find("FileName").text();
                    var y = $dataPoint.find("Lines").text();
        var z= $dataPoint.find("Branches").text();
        data2.push({ label: label, y: parseFloat(z),color: "blue" });
            data1.push({ label: label, y: parseFloat(y),color:"red" });
            });
            chart.render();
    });
     
    }
    </script>
    </head>
    <body>
    <center><div id="chartContainer" style="height: 650px; width: 100%"></div></center>
    <script src="https://canvasjs.com/assets/script/jquery-1.11.1.min.js"></script>
    <script src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>
    </body>
    </html>

    ''')
    f.close() 
    
    f= open("chart2.html","w+") # to write a new HTML page 

    f.write('''<!DOCTYPE HTML>
    <html>
    <head><title>GCC Report Response Chart 3</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <script type="text/javascript">
    window.onload = function() { 
     
    var data1 = [];
    var data2 = [];

    var chart = new CanvasJS.Chart("chartContainer", {
      animationEnabled: true,
            
            axisX:{
                    interval: 1,
        labelFontSize: 13,
        
            },
      
            // subtitles:[{
            // 	text: "GCC Chart"
            // }],
            data: [{
                    legendText: "Lines",
        axisYType: "secondary",
                    type: "stepArea",
                    showInLegend: true, 
                    //indexLabel: "{y}",
                    //indexLabelPlacement: "inside",
                    dataPoints: data1,   
                    
            },{
        legendText: "Branches",
        axisYType: "secondary",
                    type: "stepArea",
                    showInLegend: true, 
                    //indexLabel: "{y}",
                    //indexLabelPlacement: "inside",
                    dataPoints: data2,


      }]
    });
     
    $.get("xmlfile.xml", function (data) {
            $(data).find("item").each(function () {
                    var $dataPoint = jQuery(this);
                    var label = $dataPoint.find("FileName").text();
                    var y = $dataPoint.find("Lines").text();
        var z= $dataPoint.find("Branches").text();
        data2.push({ label: label, y: parseFloat(z),borderColor: "blue" });
            data1.push({ label: label, y: parseFloat(y),borderColor:"red" });
            });
            chart.render();
    });
     
    }
    </script>
    </head>
    <body>
    <center><div id="chartContainer" style="height: 650px; width: 100%"></div></center>
    <script src="https://canvasjs.com/assets/script/jquery-1.11.1.min.js"></script>
    <script src="https://canvasjs.com/assets/script/canvasjs.min.js"></script>
    </body>
    </html>

    ''')
    f.close() 
    os.startfile("http://localhost:9997\\"+"\\"+'table.html')
    os.startfile("http://localhost:9997\\"+"\\"+'chart.html')
    os.startfile("http://localhost:9997\\"+"\\"+'chart1.html')
    os.startfile("http://localhost:9997\\"+"\\"+'chart2.html')
    httpd.serve_forever()
