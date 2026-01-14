/** @odoo-module **/

odoo.define('quan_ly_khach_hang.dashboard_charts', function (require) {
    'use strict';

    const FormController = require('web.FormController');
    const rpc = require('web.rpc');

    // Load Chart.js
    function loadChartJS() {
        return new Promise((resolve) => {
            if (typeof window.Chart !== 'undefined') {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }

    // Render charts
    function renderCharts(data) {
        if (!data || typeof window.Chart === 'undefined') {
            console.warn('Cannot render charts - missing data or Chart.js');
            return;
        }

        console.log('Rendering charts with data:', data);

        // Chart 1: Trạng thái khách hàng
        try {
            const data1 = data.chart_customer_status_data ? JSON.parse(data.chart_customer_status_data) : null;
            console.log('Chart 1 data:', data1);
            if (data1 && data1.labels && data1.data && data1.data.length > 0) {
                const ctx1 = document.getElementById('chartCustomerStatus');
                if (ctx1) {
                    if (ctx1.chart) ctx1.chart.destroy();
                    ctx1.chart = new window.Chart(ctx1.getContext('2d'), {
                        type: 'pie',
                        data: {
                            labels: data1.labels,
                            datasets: [{
                                data: data1.data,
                                backgroundColor: data1.colors,
                                borderWidth: 2,
                                borderColor: '#fff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: { legend: { position: 'bottom' } }
                        }
                    });
                    console.log('Chart 1 rendered successfully');
                } else {
                    console.warn('Chart 1 canvas not found');
                }
            } else {
                console.warn('Chart 1: Invalid data', data1);
            }
        } catch(e) { console.error('Chart 1 error:', e); }

        // Chart 2: Phân loại
        try {
            const data2 = data.chart_classification_data ? JSON.parse(data.chart_classification_data) : null;
            console.log('Chart 2 data:', data2);
            if (data2 && data2.labels && data2.data && data2.data.length > 0) {
                const ctx2 = document.getElementById('chartClassification');
                if (ctx2) {
                    if (ctx2.chart) ctx2.chart.destroy();
                    ctx2.chart = new window.Chart(ctx2.getContext('2d'), {
                        type: 'doughnut',
                        data: {
                            labels: data2.labels,
                            datasets: [{
                                data: data2.data,
                                backgroundColor: data2.colors,
                                borderWidth: 2,
                                borderColor: '#fff'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: { legend: { position: 'bottom' } }
                        }
                    });
                    console.log('Chart 2 rendered successfully');
                } else {
                    console.warn('Chart 2 canvas not found');
                }
            } else {
                console.warn('Chart 2: Invalid data', data2);
            }
        } catch(e) { console.error('Chart 2 error:', e); }

        // Chart 3: Đơn hàng
        try {
            const data3 = data.chart_orders_data ? JSON.parse(data.chart_orders_data) : null;
            console.log('Chart 3 data:', data3);
            if (data3 && data3.labels && data3.data && data3.data.length > 0) {
                const ctx3 = document.getElementById('chartOrders');
                if (ctx3) {
                    if (ctx3.chart) ctx3.chart.destroy();
                    ctx3.chart = new window.Chart(ctx3.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: data3.labels,
                            datasets: [{
                                label: 'Số lượng',
                                data: data3.data,
                                backgroundColor: data3.colors,
                                borderColor: data3.colors,
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: { legend: { display: false } },
                            scales: { y: { beginAtZero: true } }
                        }
                    });
                    console.log('Chart 3 rendered successfully');
                } else {
                    console.warn('Chart 3 canvas not found');
                }
            } else {
                console.warn('Chart 3: Invalid data', data3);
            }
        } catch(e) { console.error('Chart 3 error:', e); }

        // Chart 4: Doanh thu
        try {
            const data4 = data.chart_revenue_data ? JSON.parse(data.chart_revenue_data) : null;
            console.log('Chart 4 data:', data4);
            if (data4 && data4.labels && data4.data && data4.data.length > 0) {
                const ctx4 = document.getElementById('chartRevenue');
                if (ctx4) {
                    if (ctx4.chart) ctx4.chart.destroy();
                    ctx4.chart = new window.Chart(ctx4.getContext('2d'), {
                        type: 'line',
                        data: {
                            labels: data4.labels,
                            datasets: [{
                                label: 'Doanh thu',
                                data: data4.data,
                                borderColor: data4.color,
                                backgroundColor: data4.color + '20',
                                borderWidth: 3,
                                fill: true,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: { legend: { display: true, position: 'top' } },
                            scales: { y: { beginAtZero: true } }
                        }
                    });
                    console.log('Chart 4 rendered successfully');
                } else {
                    console.warn('Chart 4 canvas not found');
                }
            } else {
                console.warn('Chart 4: Invalid data', data4);
            }
        } catch(e) { console.error('Chart 4 error:', e); }

        // Chart 5: Combined (Bar + Line với 2 trục Y)
        try {
            const data5 = data.chart_combined_data ? JSON.parse(data.chart_combined_data) : null;
            console.log('Chart 5 (Combined) data:', data5);
            if (data5 && data5.labels && data5.barData && data5.lineData) {
                const ctx5 = document.getElementById('chartCombined');
                if (ctx5) {
                    if (ctx5.chart) ctx5.chart.destroy();
                    const labels = data5.labels.map(d => {
                        if (typeof d === 'string') return d;
                        const date = new Date(d);
                        return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
                    });
                    ctx5.chart = new window.Chart(ctx5.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [
                                {
                                    type: 'bar',
                                    label: data5.barData.label,
                                    data: data5.barData.data,
                                    backgroundColor: data5.barData.color + '80',
                                    borderColor: data5.barData.color,
                                    borderWidth: 1,
                                    yAxisID: 'y'
                                },
                                {
                                    type: 'line',
                                    label: data5.lineData.label,
                                    data: data5.lineData.data,
                                    borderColor: data5.lineData.color,
                                    backgroundColor: data5.lineData.color + '20',
                                    borderWidth: 3,
                                    fill: false,
                                    tension: 0.4,
                                    pointRadius: 5,
                                    pointBackgroundColor: data5.lineData.color,
                                    yAxisID: 'y1'
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            interaction: {
                                mode: 'index',
                                intersect: false,
                            },
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'bottom'
                                }
                            },
                            scales: {
                                y: {
                                    type: 'linear',
                                    display: true,
                                    position: 'left',
                                    beginAtZero: true,
                                    title: {
                                        display: true,
                                        text: data5.barData.label
                                    }
                                },
                                y1: {
                                    type: 'linear',
                                    display: true,
                                    position: 'right',
                                    beginAtZero: true,
                                    grid: {
                                        drawOnChartArea: false,
                                    },
                                    title: {
                                        display: true,
                                        text: data5.lineData.label
                                    }
                                }
                            }
                        }
                    });
                    console.log('Chart 5 (Combined) rendered successfully');
                }
            }
        } catch(e) { console.error('Chart 5 (Combined) error:', e); }

        // Chart 6: Achievement Donut với phần trăm
        try {
            const data6 = data.chart_achievement_data ? JSON.parse(data.chart_achievement_data) : null;
            console.log('Chart 6 (Achievement) data:', data6);
            if (data6 && data6.percent !== undefined) {
                const ctx6 = document.getElementById('chartAchievement');
                if (ctx6) {
                    if (ctx6.chart) ctx6.chart.destroy();
                    
                    // Cập nhật text bên ngoài trước
                    const percentEl = document.getElementById('achievementPercent');
                    if (percentEl) percentEl.textContent = data6.percent;
                    
                    ctx6.chart = new window.Chart(ctx6.getContext('2d'), {
                        type: 'doughnut',
                        data: {
                            labels: ['Đạt được', 'Còn lại'],
                            datasets: [{
                                data: [data6.percent, Math.max(0, 100 - data6.percent)],
                                backgroundColor: [
                                    data6.color || '#667eea',
                                    '#e0e0e0'
                                ],
                                borderWidth: 0
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            cutout: '75%',
                            plugins: {
                                legend: {
                                    display: false
                                },
                                tooltip: {
                                    enabled: false
                                }
                            }
                        },
                        plugins: [{
                            id: 'centerText',
                            beforeDraw: function(chart) {
                                const ctx = chart.ctx;
                                const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
                                const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
                                
                                ctx.save();
                                ctx.font = 'bold 32px Arial';
                                ctx.fillStyle = '#2c3e50';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                ctx.fillText(data6.percent + '%', centerX, centerY);
                                ctx.restore();
                            }
                        }]
                    });
                    console.log('Chart 6 (Achievement) rendered successfully');
                }
            }
        } catch(e) { console.error('Chart 6 (Achievement) error:', e); }

        // Progress Bars
        try {
            const progressData = data.chart_progress_data ? JSON.parse(data.chart_progress_data) : null;
            console.log('Progress data:', progressData);
            if (progressData) {
                // Income progress
                const incomeBar = document.getElementById('progressIncomeBar');
                const incomePercent = document.getElementById('progressIncomePercent');
                if (incomeBar && incomePercent) {
                    incomeBar.style.width = progressData.income + '%';
                    incomePercent.textContent = progressData.income + '%';
                }

                // Orders progress
                const ordersBar = document.getElementById('progressOrdersBar');
                const ordersPercent = document.getElementById('progressOrdersPercent');
                if (ordersBar && ordersPercent) {
                    ordersBar.style.width = progressData.orders + '%';
                    ordersPercent.textContent = progressData.orders + '%';
                }

                // Customers progress
                const customersBar = document.getElementById('progressCustomersBar');
                const customersPercent = document.getElementById('progressCustomersPercent');
                if (customersBar && customersPercent) {
                    customersBar.style.width = progressData.customers + '%';
                    customersPercent.textContent = progressData.customers + '%';
                }

                // Support progress
                const supportBar = document.getElementById('progressSupportBar');
                const supportPercent = document.getElementById('progressSupportPercent');
                if (supportBar && supportPercent) {
                    supportBar.style.width = progressData.support + '%';
                    supportPercent.textContent = progressData.support + '%';
                }

                // Spending progress (trong achievement card)
                const spendingBar = document.getElementById('progressSpendingBar');
                const spendingPercent = document.getElementById('progressSpendingPercent');
                if (spendingBar && spendingPercent) {
                    const spendingValue = Math.min(100, progressData.income || 0);
                    spendingBar.style.width = spendingValue + '%';
                    spendingPercent.textContent = spendingValue + '%';
                }

                console.log('Progress bars updated successfully');
            }
        } catch(e) { console.error('Progress bars error:', e); }
    }

    // Function to fetch and render charts
    function fetchAndRenderCharts(recordId) {
        if (!recordId) {
            console.warn('No record ID provided');
            return;
        }

        loadChartJS().then(() => {
            console.log('Chart.js loaded, fetching chart data for record:', recordId);
            // Sử dụng method riêng để lấy dữ liệu chart
            rpc.query({
                model: 'qlkh.customer.dashboard',
                method: 'get_chart_data',
                args: [[recordId]],
            }).then(function(result) {
                console.log('Chart Data RPC Result:', result);
                if (result && result[0]) {
                    renderCharts(result[0]);
                } else {
                    console.warn('No chart data returned from RPC, trying read method');
                    // Fallback: thử read method
                    rpc.query({
                        model: 'qlkh.customer.dashboard',
                        method: 'read',
                        args: [[recordId], [
                    'chart_customer_status_data',
                    'chart_classification_data',
                    'chart_orders_data',
                    'chart_revenue_data',
                    'chart_combined_data',
                    'chart_achievement_data',
                    'chart_progress_data'
                ]],
                    }).then(function(readResult) {
                        console.log('Read RPC Result:', readResult);
                        if (readResult && readResult[0]) {
                            renderCharts(readResult[0]);
                        }
                    });
                }
            }).catch(function(error) {
                console.error('RPC Error:', error);
            });
        });
    }

    // Extend FormController
    FormController.include({
        init: function() {
            this._super.apply(this, arguments);
            this._chartInitialized = false;
        },

        _onRecordLoaded: function(record) {
            const result = this._super.apply(this, arguments);
            if (this.modelName === 'qlkh.customer.dashboard' && !this._chartInitialized) {
                this._chartInitialized = true;
                console.log('Customer Dashboard loaded, record:', record);
                
                // Đợi một chút để đảm bảo form đã render xong
                setTimeout(() => {
                    const recordId = record.id;
                    const recordData = record.data;
                    
                    console.log('Record ID:', recordId);
                    console.log('Record Data:', recordData);
                    
                    // Thử lấy từ record.data trước
                    if (recordData && (recordData.chart_customer_status_data || 
                                      recordData.chart_classification_data || 
                                      recordData.chart_orders_data || 
                                      recordData.chart_revenue_data)) {
                        loadChartJS().then(() => {
                            setTimeout(() => renderCharts(recordData), 500);
                        });
                    } else if (recordId) {
                        // Nếu không có trong record.data, fetch từ server
                        fetchAndRenderCharts(recordId);
                    } else {
                        // Nếu không có record ID, đợi thêm một chút
                        setTimeout(() => {
                            const newRecordId = record.id;
                            if (newRecordId) {
                                fetchAndRenderCharts(newRecordId);
                            } else {
                                console.warn('Still no record ID after delay');
                            }
                        }, 2000);
                    }
                }, 1500);
            }
            return result;
        },

        _onFieldChanged: function(event) {
            const result = this._super.apply(this, arguments);
            if (this.modelName === 'qlkh.customer.dashboard') {
                setTimeout(() => {
                    const record = this.model.get(this.handle);
                    if (record) {
                        const recordData = record.data;
                        if (recordData) {
                            loadChartJS().then(() => {
                                renderCharts(recordData);
                            });
                        }
                    }
                }, 300);
            }
            return result;
        }
    });
});
