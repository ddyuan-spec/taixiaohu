// 画像提取日志数据
const mockData = [
  { id: 'EXT-20250616001', time: '2026-06-16 14:32:18', users: 156, portraits: 1084, success: 1080, failed: 4, status: 'success', duration: '2m 34s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616002', time: '2026-06-16 13:30:05', users: 142, portraits: 994, success: 990, failed: 4, status: 'success', duration: '2m 18s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616003', time: '2026-06-16 12:28:42', users: 138, portraits: 966, success: 963, failed: 3, status: 'success', duration: '2m 12s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616004', time: '2026-06-16 11:25:19', users: 145, portraits: 1015, success: 1012, failed: 3, status: 'success', duration: '2m 28s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616005', time: '2026-06-16 10:22:55', users: 132, portraits: 924, success: 920, failed: 4, status: 'success', duration: '2m 05s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616006', time: '2026-06-16 09:20:31', users: 128, portraits: 896, success: 894, failed: 2, status: 'success', duration: '1m 58s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616007', time: '2026-06-16 08:18:07', users: 125, portraits: 875, success: 872, failed: 3, status: 'success', duration: '1m 52s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616008', time: '2026-06-16 07:15:43', users: 118, portraits: 826, success: 824, failed: 2, status: 'success', duration: '1m 48s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616009', time: '2026-06-16 06:12:20', users: 110, portraits: 770, success: 768, failed: 2, status: 'success', duration: '1m 42s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616010', time: '2026-06-16 05:10:56', users: 105, portraits: 735, success: 733, failed: 2, status: 'success', duration: '1m 38s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616011', time: '2026-06-16 04:08:32', users: 98, portraits: 686, success: 684, failed: 2, status: 'success', duration: '1m 35s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250616012', time: '2026-06-16 03:05:09', users: 92, portraits: 644, success: 642, failed: 2, status: 'success', duration: '1m 28s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250615013', time: '2026-06-15 23:55:44', users: 88, portraits: 616, success: 614, failed: 2, status: 'success', duration: '1m 25s', operator: 'admin', note: '手动触发-全量' },
  { id: 'EXT-20250615014', time: '2026-06-15 18:30:22', users: 85, portraits: 595, success: 593, failed: 2, status: 'success', duration: '1m 22s', operator: 'system', note: '定时任务-每小时' },
  { id: 'EXT-20250615015', time: '2026-06-15 12:00:00', users: 80, portraits: 560, success: 558, failed: 2, status: 'failed', duration: '5m 10s', operator: 'system', note: '连接超时' },
];

let currentData = [...mockData];

// 状态映射
const statusMap = {
  success: { label: '成功', class: 'badge-success' },
  running: { label: '进行中', class: 'badge-running' },
  failed: { label: '失败', class: 'badge-failed' },
  pending: { label: '等待中', class: 'badge-pending' }
};

// 渲染表格
function renderTable(data) {
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  if (data.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="10">
          <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="9" y1="9" x2="15" y2="15"></line>
              <line x1="15" y1="9" x2="9" y2="15"></line>
            </svg>
            <p>暂无匹配记录</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  data.forEach(row => {
    const status = statusMap[row.status] || statusMap.pending;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><code style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--accent);">${row.id}</code></td>
      <td>${row.time}</td>
      <td>${row.users.toLocaleString()}</td>
      <td>${row.portraits.toLocaleString()}</td>
      <td style="color: var(--accent2); font-weight: 600;">${row.success.toLocaleString()}</td>
      <td style="color: ${row.failed > 0 ? 'var(--accent-danger)' : 'var(--muted)'}; font-weight: 600;">${row.failed.toLocaleString()}</td>
      <td><span class="badge ${status.class}"><span class="badge-dot"></span>${status.label}</span></td>
      <td>${row.duration}</td>
      <td>${row.operator}</td>
      <td style="color: var(--muted); font-size: 0.85rem;">${row.note}</td>
    `;
    tbody.appendChild(tr);
  });

  document.getElementById('totalRecords').textContent = data.length;
}

// 应用筛选
function applyFilters() {
  const dateVal = document.getElementById('filterDate').value;
  const statusVal = document.getElementById('filterStatus').value;
  const searchVal = document.getElementById('filterSearch').value.toLowerCase();

  currentData = mockData.filter(row => {
    const matchDate = !dateVal || row.time.startsWith(dateVal.replace(/-/g, ''));
    const matchStatus = !statusVal || row.status === statusVal;
    const matchSearch = !searchVal ||
      row.id.toLowerCase().includes(searchVal) ||
      row.note.toLowerCase().includes(searchVal) ||
      row.operator.toLowerCase().includes(searchVal);
    return matchDate && matchStatus && matchSearch;
  });

  renderTable(currentData);
}

// 刷新数据
function refreshData() {
  showToast('数据已刷新', 'success');
  applyFilters();
}

// Modal 控制
function openModal() {
  document.getElementById('triggerModal').classList.add('active');
}

function closeModal() {
  document.getElementById('triggerModal').classList.remove('active');
}

// 确认触发
function confirmTrigger() {
  const btn = document.getElementById('confirmBtn');
  btn.disabled = true;
  btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite;"><circle cx="12" cy="12" r="10" stroke-dasharray="60" stroke-dashoffset="20"></circle></svg> 触发中...`;

  setTimeout(() => {
    // 添加新任务到数据
    const now = new Date();
    const timeStr = now.getFullYear() + '-' +
      String(now.getMonth() + 1).padStart(2, '0') + '-' +
      String(now.getDate()).padStart(2, '0') + ' ' +
      String(now.getHours()).padStart(2, '0') + ':' +
      String(now.getMinutes()).padStart(2, '0') + ':' +
      String(now.getSeconds()).padStart(2, '0');

    const newTask = {
      id: 'EXT-' + now.getFullYear() + String(now.getMonth() + 1).padStart(2, '0') + String(now.getDate()).padStart(2, '0') + String(Math.floor(Math.random() * 900) + 100),
      time: timeStr,
      users: 0,
      portraits: 0,
      success: 0,
      failed: 0,
      status: 'running',
      duration: '-',
      operator: 'admin',
      note: '手动触发'
    };

    mockData.unshift(newTask);
    currentData = [...mockData];
    renderTable(currentData);
    updateStats();

    // 模拟任务完成
    setTimeout(() => {
      newTask.status = 'success';
      newTask.users = Math.floor(Math.random() * 50) + 100;
      newTask.portraits = newTask.users * 7;
      newTask.success = newTask.portraits - Math.floor(Math.random() * 5);
      newTask.failed = newTask.portraits - newTask.success;
      newTask.duration = Math.floor(Math.random() * 60 + 90) + 's';
      renderTable(currentData);
      updateStats();
      showToast(`任务 ${newTask.id} 已完成`, 'success');
    }, 3000);

    btn.disabled = false;
    btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> 确认触发`;
    closeModal();
    showToast('画像拉取任务已触发', 'success');
  }, 800);
}

// Toast 提示
function showToast(message, type) {
  const toast = document.getElementById('toast');
  const content = document.getElementById('toastContent');
  content.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// 更新统计数据
function updateStats() {
  const today = '2026-06-16';
  const todayData = mockData.filter(d => d.time.startsWith(today.replace(/-/g, '')));
  const successData = todayData.filter(d => d.status === 'success');

  const totalUsers = successData.reduce((sum, d) => sum + d.users, 0);
  const totalPortraits = successData.reduce((sum, d) => sum + d.portraits, 0);
  const successRate = todayData.length > 0
    ? ((successData.length / todayData.length) * 100).toFixed(1) + '%'
    : '0%';

  document.getElementById('statCount').textContent = todayData.length;
  document.getElementById('statUsers').textContent = totalUsers.toLocaleString();
  document.getElementById('statPortraits').textContent = totalPortraits.toLocaleString();
  document.getElementById('statSuccess').textContent = successRate;
}

// 点击遮罩关闭 modal
document.getElementById('triggerModal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

// 初始化
renderTable(currentData);
updateStats();
