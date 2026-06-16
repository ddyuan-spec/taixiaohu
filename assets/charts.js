(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();

  // --- Chart: Trend Line (近7天画像提取趋势) ---
  var trendChart = echarts.init(document.getElementById('trendChart'), null, { renderer: 'svg' });
  trendChart.setOption({
    animation: false,
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      backgroundColor: bg2,
      borderColor: rule,
      textStyle: { color: ink }
    },
    legend: {
      data: ['提取画像量', '提取用户数'],
      bottom: 0,
      textStyle: { color: muted }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['06-10', '06-11', '06-12', '06-13', '06-14', '06-15', '06-16'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: rule, type: 'dashed' } },
      axisLabel: { color: muted }
    },
    series: [
      {
        name: '提取画像量',
        type: 'line',
        data: [6200, 6850, 7100, 7450, 7800, 8120, 8632],
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: accent, width: 3 },
        itemStyle: { color: accent },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: accent + '33' },
              { offset: 1, color: accent + '05' }
            ]
          }
        }
      },
      {
        name: '提取用户数',
        type: 'line',
        data: [890, 950, 1020, 1080, 1150, 1180, 1248],
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: accent2, width: 3 },
        itemStyle: { color: accent2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: accent2 + '33' },
              { offset: 1, color: accent2 + '05' }
            ]
          }
        }
      }
    ]
  });
  window.addEventListener('resize', function() { trendChart.resize(); });

  // --- Chart: Status Pie (提取状态分布) ---
  var statusChart = echarts.init(document.getElementById('statusChart'), null, { renderer: 'svg' });
  statusChart.setOption({
    animation: false,
    tooltip: {
      trigger: 'item',
      appendToBody: true,
      backgroundColor: bg2,
      borderColor: rule,
      textStyle: { color: ink },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      bottom: 0,
      textStyle: { color: muted }
    },
    series: [
      {
        name: '提取状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: bg2,
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: ink
          }
        },
        labelLine: { show: false },
        data: [
          { value: 186, name: '成功', itemStyle: { color: '#059669' } },
          { value: 3, name: '失败', itemStyle: { color: '#dc2626' } },
          { value: 2, name: '进行中', itemStyle: { color: '#2563eb' } },
          { value: 1, name: '等待中', itemStyle: { color: '#d97706' } }
        ]
      }
    ]
  });
  window.addEventListener('resize', function() { statusChart.resize(); });
})();
