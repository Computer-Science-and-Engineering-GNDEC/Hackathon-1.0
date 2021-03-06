/*Sparkline Init*/
  
$(document).ready(function() {
   "use strict";
   
   var sparklineLogin = function() { 
		if( $('#sparkline_1').length > 0 ){
			$("#sparkline_1").sparkline([2,4,4,6,8,5,6,4,8,6,6,2 ], {
				type: 'line',
				width: '100%',
				height: '50',
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
			$("#sparkline_2").sparkline([0,2,8,6,8,5,6,4,8,6,6,2 ], {
				type: 'bar',
				width: '100%',
				height: '50',
				barWidth: '5',
				barSpacing: '5',
				barColor: 'rgba(46,205,153,.6)',
				highlightSpotColor: 'rgba(46,205,153,.6)'
			});
		}	
		if( $('#sparkline_3').length > 0 ){
			$("#sparkline_3").sparkline([20,4,4], {
				type: 'pie',
				width: '50',
				height: '50',
				sliceColors: ['rgba(240,197,65, 0.6)', 'rgba(46,205,153,.6)','rgba(78,157,230,.6)']
			});
		}
		if( $('#sparkline_4').length > 0 ){
			$("#sparkline_4").sparkline([5,6,2,8,9,4,7,10,5,4,2], {
			type: 'bar',
			height: '200',
			width: '100%',
			barWidth: 10,
			barSpacing: 5,
			barColor: 'rgba(46,205,153,.6)',
			});
		}	
		
		if( $('#sparkline_5').length > 0 ){
			$('#sparkline_5').sparkline([5, 6, 2, 9, 4, 7, 5, 8, 5,4], {
				type: 'bar',
				height: '200',
				width: '100%',
				barWidth: '10',
				barSpacing: '5',
				barColor: 'rgba(46,205,153,.6)'
			});
			$('#sparkline_5').sparkline([5, 6, 2, 9, 4, 7, 10, 12,4,7,10], {
				type: 'line',
				height: '200',
				width: '100%',
				lineColor: '#2ecd99',
				fillColor: 'rgba(46,205,153,.6)',
				minSpotColor: '#2ecd99',
				maxSpotColor: '#2ecd99',
				spotColor: '#2ecd99',
				highlightLineColor: 'rgba(0, 0, 0, 0.6)',
				highlightSpotColor: '#2ecd99'
			});
		}
		
		if( $('#sparkline_6').length > 0 ){
			$("#sparkline_6").sparkline([0, 23, 43, 35, 44, 45, 56, 37, 40, 45, 56, 7, 10], {
				type: 'line',
				width: '100%',
				height: '200',
				lineColor: '#2ecd99',
				fillColor: 'rgba(46,205,153,.6)',
				minSpotColor: '#2ecd99',
				maxSpotColor: '#2ecd99',
				spotColor: '#2ecd99',
				highlightLineColor: 'rgba(0, 0, 0, 0.6)',
				highlightSpotColor: '#2ecd99'
			});
		}
		if( $('#sparkline_7').length > 0 ){
			$('#sparkline_7').sparkline([15, 23, 55, 35, 54, 45, 66, 47, 30], {
				type: 'line',
				width: '100%',
				height: '200',
				chartRangeMax: 50,
				lineColor: '#2ecd99',
				fillColor: 'rgba(46,205,153,.6)',
				minSpotColor: '#2ecd99',
				maxSpotColor: '#2ecd99',
				spotColor: '#2ecd99',
				highlightLineColor: 'rgba(0, 0, 0, 0.6)',
				highlightSpotColor: '#2ecd99'
			});
			$('#sparkline_7').sparkline([0, 13, 10, 14, 15, 10, 18, 20, 0], {
				type: 'line',
				width: '100%',
				height: '200',
				chartRangeMax: 40,
				lineColor: 'rgba(240,197,65, 0.6)',
				fillColor: 'rgba(240,197,65, 0.6)',
				composite: true,
				lineColor: '#f0c541',
				fillColor: 'rgba(240,197,65, 0.6)',
				minSpotColor: '#f0c541',
				maxSpotColor: '#f0c541',
				spotColor: '#f0c541',
				highlightLineColor: 'rgba(0, 0, 0, 0.6)',
				highlightSpotColor: '#f0c541'
			});
			if( $('#sparkline_8').length > 0 ){
				$("#sparkline_8").sparkline([20,10,4], {
					type: 'pie',
					width: '200',
					height: '200',
					sliceColors: ['rgba(240,197,65, 0.6)', 'rgba(46,205,153,.6)','rgba(78,157,230,.6)']
				});
			}
		}	
   }
    var sparkResize;
 
        $(window).resize(function(e) {
            clearTimeout(sparkResize);
            sparkResize = setTimeout(sparklineLogin, 200);
        });
        sparklineLogin();

});