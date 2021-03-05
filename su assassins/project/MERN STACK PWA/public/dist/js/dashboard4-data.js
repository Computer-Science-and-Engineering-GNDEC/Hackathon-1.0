/*Dashboard Init*/
 
"use strict"; 

/*****Ready function start*****/
$(document).ready(function(){
	$('#statement').DataTable({
		"bFilter": false,
		"bLengthChange": false,
		"bPaginate": false,
		"bInfo": false,
	});
	if($('#chart_1').length > 0)
		// Line Chart
		Morris.Line({
			// ID of the element in which to draw the chart.
			element: 'chart_1',
			// Chart data records -- each entry in this array corresponds to a point on
			// the chart.
			data: [{
				d: '2012-10-01',
				visits: 802
			}, {
				d: '2012-10-02',
				visits: 783
			}, {
				d: '2012-10-03',
				visits: 820
			}, {
				d: '2012-10-04',
				visits: 839
			}, {
				d: '2012-10-05',
				visits: 792
			}, {
				d: '2012-10-06',
				visits: 859
			}, {
				d: '2012-10-07',
				visits: 790
			}, {
				d: '2012-10-08',
				visits: 1680
			}, {
				d: '2012-10-09',
				visits: 1592
			}, {
				d: '2012-10-10',
				visits: 1420
			}, {
				d: '2012-10-11',
				visits: 882
			}, {
				d: '2012-10-12',
				visits: 889
			}, {
				d: '2012-10-13',
				visits: 819
			}, {
				d: '2012-10-14',
				visits: 849
			}, {
				d: '2012-10-15',
				visits: 870
			}, {
				d: '2012-10-16',
				visits: 1063
			}, {
				d: '2012-10-17',
				visits: 1192
			}, {
				d: '2012-10-18',
				visits: 1224
			}, {
				d: '2012-10-19',
				visits: 1329
			}, {
				d: '2012-10-20',
				visits: 1329
			}, {
				d: '2012-10-21',
				visits: 1239
			}, {
				d: '2012-10-22',
				visits: 1190
			}, {
				d: '2012-10-23',
				visits: 1312
			}, {
				d: '2012-10-24',
				visits: 1293
			}, {
				d: '2012-10-25',
				visits: 1283
			}, {
				d: '2012-10-26',
				visits: 1248
			}, {
				d: '2012-10-27',
				visits: 1323
			}, {
				d: '2012-10-28',
				visits: 1390
			}, {
				d: '2012-10-29',
				visits: 1420
			}, {
				d: '2012-10-30',
				visits: 1529
			}, {
				d: '2012-10-31',
				visits: 1892
			}, ],
			// The name of the data record attribute that contains x-visitss.
			xkey: 'd',
			// A list of names of data record attributes that contain y-visitss.
			ykeys: ['visits'],
			// Labels for the ykeys -- will be displayed when you hover over the
			// chart.
			labels: ['Visits'],
			// Disables line smoothing
			pointSize: 1,
			pointStrokeColors:['#2ecd99'],
			behaveLikeLine: true,
			grid:false,
			gridTextColor:'#878787',
			lineWidth: 2,
			smooth: true,
			hideHover: 'auto',
			lineColors: ['#2ecd99'],
			resize: true,
			gridTextFamily:"Poppins"
		});

	if( $('#chart_2').length > 0 ){
		var ctx2 = document.getElementById("chart_2").getContext("2d");
		var data2 = {
			labels: ["January", "February", "March", "April", "May", "June", "July"],
			datasets: [
				{
					label: "My First dataset",
					backgroundColor: "rgba(240,197,65,.6)",
					borderColor: "rgba(240,197,65,.6)",
					data: [10, 30, 80, 61, 26, 75, 40]
				},
				{
					label: "My Second dataset",
					backgroundColor: "rgba(46,205,153,.6)",
					borderColor: "rgba(46,205,153,.6)",
					data: [28, 48, 40, 19, 86, 27, 90]
				},
				{
					label: "My Third dataset",
					backgroundColor: "rgba(78,157,230,.6)",
					borderColor: "rgba(78,157,230,.6)",
					data: [8, 28, 50, 29, 76, 77, 40]
				}
			]
		};
		
		var hBar = new Chart(ctx2, {
			type:"bar",
			data:data2,
			
			options: {
				tooltips: {
					mode:"label"
				},
				scales: {
					yAxes: [{
						stacked: true,
						gridLines: {
							color: "rgba(135,135,135,0)",
						},
						ticks: {
							fontFamily: "Poppins",
							fontColor:"#878787"
						}
					}],
					xAxes: [{
						stacked: true,
						gridLines: {
							color: "rgba(135,135,135,0)",
						},
						ticks: {
							fontFamily: "Poppins",
							fontColor:"#878787"
						}
					}],
					
				},
				elements:{
					point: {
						hitRadius:40
					}
				},
				animation: {
					duration:	3000
				},
				responsive: true,
				maintainAspectRatio:false,
				legend: {
					display: false,
				},
				
				tooltip: {
					backgroundColor:'rgba(33,33,33,1)',
					cornerRadius:0,
					footerFontFamily:"'Poppins'"
				}
				
			}
		});
	}
	if($('#morris_donut_chart').length > 0) {
		// Donut Chart
		Morris.Donut({
			element: 'morris_donut_chart',
			data: [{
				label: "Accident and emergency",
				value: 12
			}, {
				label: "Diagnostic imaging",
				value: 30
			}, {
				label: "Discharge lounge",
				value: 20
			}],
			colors: ['rgba(46,205,153,.6)', 'rgba(240,197,65,.6)', 'rgba(237,111,86,.6)'],
			resize: true,
			labelColor: '#878787',
		});
		$("div svg text").attr("style","font-family: Poppins").attr("font-weight","400");
	}	
	if($('#appoinmnts_chart').length > 0) {
		// Area Chart
		var data=[{
            period: '01',
            iphone: 180,
        }, {
            period: '02',
            iphone: 105,
        },
         {
            period: '03',
            iphone: 250,
        },
		 {
            period: '04',
            iphone: 160,
        },
		 {
            period: '05',
            iphone: 130,
        },
		{
            period: '06',
            iphone: 155,
        },
		{
            period: '07',
            iphone: 150,
        },
		{
            period: '08',
            iphone: 110,
        },
		{
            period: '09',
            iphone: 170,
        },
		{
            period: '10',
            iphone: 150,
        },
		{
            period: '11',
            iphone: 150,
        },
		{
            period: '12',
            iphone: 150,
        },
		{
            period: '13',
            iphone: 150,
        },
		{
            period: '14',
            iphone: 150,
        },
		{
            period: '15',
            iphone: 160,
        },
		{
            period: '16',
            iphone: 180,
        }, {
            period: '17',
            iphone: 105,
        },
         {
            period: '18',
            iphone: 250,
        },
		 {
            period: '19',
            iphone: 160,
        },
		 {
            period: '20',
            iphone: 130,
        },
		{
            period: '21',
            iphone: 155,
        },
		{
            period: '22',
            iphone: 150,
        },
		{
            period: '23',
            iphone: 110,
        },
		{
            period: '24',
            iphone: 170,
        },
		{
            period: '25',
            iphone: 150,
        },
		{
            period: '26',
            iphone: 150,
        },
		{
            period: '27',
            iphone: 150,
        },
		{
            period: '28',
            iphone: 150,
        },
		{
            period: '29',
            iphone: 150,
        },
		{
            period: '30',
            iphone: 160,
        }];
		var areaChart = Morris.Area({
				element: 'appoinmnts_chart',
				data: data,
				xkey: 'period',
				ykeys: ['iphone'],
				labels: ['iPhone'],
				pointSize: 3,
				lineWidth: 2,
				grid: false,
				pointStrokeColors:['#2ecd99'],
				pointFillColors:['#ffffff'],
				behaveLikeLine: true,
				smooth: false,
				hideHover: 'auto',
				lineColors: ['#2ecd99'],
				resize: true,
				gridTextColor:'#878787',
				gridTextFamily:"Poppins",
				parseTime: false,
				fillOpacity:0.6
			});	
	}
	
});
/*****Ready function end*****/

/*****Load function start*****/
$(window).load(function(){
	window.setTimeout(function(){
		$.toast({
			heading: 'Welcome to Philbert',
			text: 'Use the predefined ones, or specify a custom position object.',
			position: 'top-right',
			loaderBg:'#f0c541',
			icon: 'success',
			hideAfter: 3500, 
			stack: 6
		});
	}, 3000);
});
/*****Load function* end*****/

var sparklineLogin = function() { 
	if( $('#sparkline_1').length > 0 ){
		$("#sparkline_1").sparkline([2,4,4,6,8,5,6,4,8,6,6,2 ], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}	
	if( $('#sparkline_2').length > 0 ){
		$("#sparkline_2").sparkline([0,2,8,6,8], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}	
	if( $('#sparkline_3').length > 0 ){
		$("#sparkline_3").sparkline([0, 23, 43, 35, 44, 45, 56, 37, 40, 45, 56, 7, 10], {
			type: 'line',
			width: '100%',
			height: '35',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}
	if( $('#sparkline_4').length > 0 ){
		$("#sparkline_4").sparkline([2,4,4,6,8,5,6,4,8,6,6,2 ], {
			type: 'line',
			width: '100%',
			height: '45',
			lineColor: '#2ecd99',
			fillColor: 'rgba(46,205,153,.6)',
			minSpotColor: '#2ecd99',
			maxSpotColor: '#2ecd99',
			spotColor: '#2ecd99',
			highlightLineColor: 'rgba(0, 0, 0, 0.6)',
			highlightSpotColor: '#2ecd99'
		});
	}
}
var sparkResize;
	$(window).resize(function(e) {
		clearTimeout(sparkResize);
		sparkResize = setTimeout(sparklineLogin, 200);
	});
sparklineLogin();