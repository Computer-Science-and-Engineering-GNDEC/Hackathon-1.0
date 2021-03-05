/*Dashboard Init*/
 
"use strict"; 

/*****Ready function start*****/
$(document).ready(function(){
	if($('#morris_extra_bar_chart').length > 0)
	// Morris bar chart
	Morris.Bar({
		element: 'morris_extra_bar_chart',
		data: [{
			y: '2006',
			a: 100,
			b: 90,
			c: 60
		}, {
			y: '2007',
			a: 75,
			b: 65,
			c: 40
		}, {
			y: '2008',
			a: 50,
			b: 40,
			c: 30
		}, {
			y: '2009',
			a: 75,
			b: 65,
			c: 40
		}, {
			y: '2010',
			a: 50,
			b: 40,
			c: 30
		}, {
			y: '2011',
			a: 75,
			b: 65,
			c: 40
		}, {
			y: '2012',
			a: 100,
			b: 90,
			c: 40
		}],
		xkey: 'y',
		ykeys: ['a', 'b', 'c'],
		labels: ['A', 'B', 'C'],
		barColors:['#2ecd99', '#f0c541', '#ed6f56'],
		barOpacity:.6,
		hideHover: 'auto',
		grid: false,
		resize: true,
		gridTextColor:'#878787',
		gridTextFamily:"Poppins"
	});

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
	if( $('#sparkline_6').length > 0 ){
		$("#sparkline_6").sparkline([12,4,7,3,8,6,8,5,6,4,8,6,6,2 ], {
			type: 'bar',
			width: '100%',
			height: '124',
			barWidth: '10',
			resize: true,
			barSpacing: '10',
			barColor: 'rgba(46,205,153,.6)',
			highlightSpotColor: '#2ecd99'
		});
	}	
	if( $('#sparkline_7').length > 0 ){
		$("#sparkline_7").sparkline([20,4,4], {
			type: 'pie',
			width: '100',
			height: '100',
			sliceColors: ['rgba(240,197,65, 0.6)', 'rgba(46,205,153,.6)','rgba(78,157,230,.6)']
		});
	}	
}
var sparkResize;
	$(window).resize(function(e) {
		clearTimeout(sparkResize);
		sparkResize = setTimeout(sparklineLogin, 200);
	});
sparklineLogin();