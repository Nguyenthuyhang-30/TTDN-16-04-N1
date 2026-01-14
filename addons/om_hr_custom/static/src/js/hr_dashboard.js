/** @odoo-module **/

odoo.define('om_hr_custom.dashboard_charts', function (require) {
    'use strict';

    const FormController = require('web.FormController');
    const rpc = require('web.rpc');

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

    function renderCharts(data) {
        if (!data || typeof window.Chart === 'undefined') {
            console.warn('Cannot render HR charts - missing data or Chart.js');
            return;
        }

        console.log('Rendering HR charts with data:', data);

        // Chart 1: Trạng thái nhân viên
        try {
            const data1 = data.chart_employee_status_data ? JSON.parse(data.chart_employee_status_data) : null;
            if (data1 && data1.labels && data1.data && data1.data.length > 0) {
                const ctx1 = document.getElementById('chartEmployeeStatus');
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
                }
            }
        } catch(e) { console.error('HR Chart 1 error:', e); }

        // Chart 2: Vai trò
        try {
            const data2 = data.chart_role_data ? JSON.parse(data.chart_role_data) : null;
            if (data2 && data2.labels && data2.data && data2.data.length > 0) {
                const ctx2 = document.getElementById('chartRole');
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
                }
            }
        } catch(e) { console.error('HR Chart 2 error:', e); }

        // Chart 3: Phân quyền
        try {
            const data3 = data.chart_permissions_data ? JSON.parse(data.chart_permissions_data) : null;
            if (data3 && data3.labels && data3.data && data3.data.length > 0) {
                const ctx3 = document.getElementById('chartPermissions');
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
                }
            }
        } catch(e) { console.error('HR Chart 3 error:', e); }
    }

    function fetchAndRenderCharts(recordId) {
        if (!recordId) return;
        loadChartJS().then(() => {
            rpc.query({
                model: 'om.hr.dashboard',
                method: 'get_chart_data',
                args: [[recordId]],
            }).then(function(result) {
                if (result && result[0]) {
                    renderCharts(result[0]);
                } else {
                    rpc.query({
                        model: 'om.hr.dashboard',
                        method: 'read',
                        args: [[recordId], [
                            'chart_employee_status_data',
                            'chart_role_data',
                            'chart_permissions_data'
                        ]],
                    }).then(function(readResult) {
                        if (readResult && readResult[0]) {
                            renderCharts(readResult[0]);
                        }
                    });
                }
            });
        });
    }

    FormController.include({
        init: function() {
            this._super.apply(this, arguments);
            this._hrChartInitialized = false;
        },

        _onRecordLoaded: function(record) {
            const result = this._super.apply(this, arguments);
            if (this.modelName === 'om.hr.dashboard' && !this._hrChartInitialized) {
                this._hrChartInitialized = true;
                setTimeout(() => {
                    const recordId = record.id;
                    const recordData = record.data;
                    if (recordData && (recordData.chart_employee_status_data || 
                                      recordData.chart_role_data || 
                                      recordData.chart_permissions_data)) {
                        loadChartJS().then(() => {
                            setTimeout(() => renderCharts(recordData), 500);
                        });
                    } else if (recordId) {
                        fetchAndRenderCharts(recordId);
                    } else {
                        setTimeout(() => {
                            const newRecordId = record.id;
                            if (newRecordId) fetchAndRenderCharts(newRecordId);
                        }, 2000);
                    }
                }, 1500);
            }
            return result;
        }
    });
});
