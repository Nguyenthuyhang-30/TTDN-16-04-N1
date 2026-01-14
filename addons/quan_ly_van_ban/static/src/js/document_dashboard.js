/** @odoo-module **/

odoo.define('quan_ly_van_ban.dashboard_charts', function (require) {
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
            console.warn('Cannot render Doc charts - missing data or Chart.js');
            return;
        }

        console.log('Rendering Doc charts with data:', data);

        // Chart 1: Văn bản đi
        try {
            const data1 = data.chart_outgoing_status_data ? JSON.parse(data.chart_outgoing_status_data) : null;
            if (data1 && data1.labels && data1.data && data1.data.length > 0) {
                const ctx1 = document.getElementById('chartOutgoing');
                if (ctx1) {
                    if (ctx1.chart) ctx1.chart.destroy();
                    ctx1.chart = new window.Chart(ctx1.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: data1.labels,
                            datasets: [{
                                label: 'Số lượng',
                                data: data1.data,
                                backgroundColor: data1.colors,
                                borderColor: data1.colors,
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
        } catch(e) { console.error('Doc Chart 1 error:', e); }

        // Chart 2: Văn bản đến
        try {
            const data2 = data.chart_incoming_status_data ? JSON.parse(data.chart_incoming_status_data) : null;
            if (data2 && data2.labels && data2.data && data2.data.length > 0) {
                const ctx2 = document.getElementById('chartIncoming');
                if (ctx2) {
                    if (ctx2.chart) ctx2.chart.destroy();
                    ctx2.chart = new window.Chart(ctx2.getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: data2.labels,
                            datasets: [{
                                label: 'Số lượng',
                                data: data2.data,
                                backgroundColor: data2.colors,
                                borderColor: data2.colors,
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
        } catch(e) { console.error('Doc Chart 2 error:', e); }

        // Chart 3: Quy trình duyệt
        try {
            const data3 = data.chart_approval_data ? JSON.parse(data.chart_approval_data) : null;
            if (data3 && data3.labels && data3.data && data3.data.length > 0) {
                const ctx3 = document.getElementById('chartApproval');
                if (ctx3) {
                    if (ctx3.chart) ctx3.chart.destroy();
                    ctx3.chart = new window.Chart(ctx3.getContext('2d'), {
                        type: 'pie',
                        data: {
                            labels: data3.labels,
                            datasets: [{
                                data: data3.data,
                                backgroundColor: data3.colors,
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
        } catch(e) { console.error('Doc Chart 3 error:', e); }

        // Chart 4: Chữ ký số
        try {
            const data4 = data.chart_signature_data ? JSON.parse(data.chart_signature_data) : null;
            if (data4 && data4.labels && data4.data && data4.data.length > 0) {
                const ctx4 = document.getElementById('chartSignature');
                if (ctx4) {
                    if (ctx4.chart) ctx4.chart.destroy();
                    ctx4.chart = new window.Chart(ctx4.getContext('2d'), {
                        type: 'doughnut',
                        data: {
                            labels: data4.labels,
                            datasets: [{
                                data: data4.data,
                                backgroundColor: data4.colors,
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
        } catch(e) { console.error('Doc Chart 4 error:', e); }

        // Chart 5: Xu hướng
        try {
            const data5 = data.chart_trend_data ? JSON.parse(data.chart_trend_data) : null;
            if (data5 && data5.labels && data5.datasets && data5.datasets.length > 0) {
                const ctx5 = document.getElementById('chartTrend');
                if (ctx5) {
                    if (ctx5.chart) ctx5.chart.destroy();
                    const datasets = data5.datasets.map(function(ds) {
                        return {
                            label: ds.label,
                            data: ds.data,
                            borderColor: ds.color,
                            backgroundColor: ds.color + '20',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        };
                    });
                    ctx5.chart = new window.Chart(ctx5.getContext('2d'), {
                        type: 'line',
                        data: {
                            labels: data5.labels,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            plugins: { legend: { display: true, position: 'top' } },
                            scales: { y: { beginAtZero: true } }
                        }
                    });
                }
            }
        } catch(e) { console.error('Doc Chart 5 error:', e); }
    }

    function fetchAndRenderCharts(recordId) {
        if (!recordId) return;
        loadChartJS().then(() => {
            rpc.query({
                model: 'om.document.dashboard',
                method: 'get_chart_data',
                args: [[recordId]],
            }).then(function(result) {
                if (result && result[0]) {
                    renderCharts(result[0]);
                } else {
                    rpc.query({
                        model: 'om.document.dashboard',
                        method: 'read',
                        args: [[recordId], [
                            'chart_outgoing_status_data',
                            'chart_incoming_status_data',
                            'chart_approval_data',
                            'chart_signature_data',
                            'chart_trend_data'
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
            this._docChartInitialized = false;
        },

        _onRecordLoaded: function(record) {
            const result = this._super.apply(this, arguments);
            if (this.modelName === 'om.document.dashboard' && !this._docChartInitialized) {
                this._docChartInitialized = true;
                setTimeout(() => {
                    const recordId = record.id;
                    const recordData = record.data;
                    if (recordData && (recordData.chart_outgoing_status_data || 
                                      recordData.chart_incoming_status_data || 
                                      recordData.chart_approval_data || 
                                      recordData.chart_signature_data || 
                                      recordData.chart_trend_data)) {
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
