$(document).ready(function(){

    var table = $("#log_table");
    table.bootstrapTable({
        search: true,
        pagination: true,
        sidePagination: 'server',
        url: 'ajax/getitems',
        classes: 'table table-striped table-hover',
        showRefresh: true,
        showColumns: true,
        columns : [{
           field: 'id',
           title: 'Log Id',
           sortable: true
        },
        {
           field: 'site_name',
           title: 'Site',
           sortable: true
        },
        {
           field: 'start_time',
           title: 'Start Time',
           sortable: true
        },
        {
           field: 'end_time',
           title: 'End Time',
           sortable: true
        },
        {
           field: 'urls_parsed',
           title: 'Urls Parsed',
           sortable: true
        },
        {
           field: 'urls_scraped',
           title: 'Urls Scraped',
           sortable: true
        },
        {
           field: 'urls_dropped',
           title: 'Urls Dropped',
           sortable: true
        },
        {
           field: 'urls_stored',
           title: 'Urls Stored',
           sortable: true
        },
        {
           field: 'shutdown_reason',
           title: 'Status',
           sortable: true
        }]
    });

});
