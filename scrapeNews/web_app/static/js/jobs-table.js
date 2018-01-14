$(document).ready(function(){

    var pendingJobsTable = $("#pending_jobs_table");
    var completedJobsTable = $("#completed_jobs_table");
    var runningJobsTable = $("#running_jobs_table");

    var runningColumns = [];
    var completedColumns = [];
    var pendingColumns = [];

    var jobColumn = {
        field: 'job_id',
        title: 'Job#',
        sortable: false,
        formatter: function(value, row, index, field){
            return '<a href="/logfiles/scrapeNews/' + row['spider_name'] + "/" + value  + '.log" title="Click to View Log">' + value + '</a>';
        }
    };

    var spiderColumn = {
        field: 'spider_name',
        title: 'Spider Name',
        sortable: false
    }

    var startTimeColumn = {
        field: 'start_time',
        title: 'Start Time',
        sortable: false
    };

    var endTimeColumn = {
        field: 'end_time',
        title: 'End Time',
        sortable: false
    };

    pendingColumns.push(jobColumn);
    pendingColumns.push(spiderColumn);


    runningColumns.push(jobColumn);
    runningColumns.push(spiderColumn);
    runningColumns.push(startTimeColumn);

    completedColumns.push(jobColumn);
    completedColumns.push(spiderColumn);
    completedColumns.push(startTimeColumn);
    completedColumns.push(endTimeColumn);

    var runningOptions = {
       search: false,
       pagination: true,
       classes: 'table table-striped table-hover',
       data: [],
       columns: runningColumns
    };

    var completedOptions = {
       search: false,
       pagination: false,
       classes: 'table table-striped table-hover',
       data: [],
       columns: completedColumns
    };

    var pendingOptions = {
       search: false,
       pagination: false,
       classes: 'table table-striped table-hover',
       data: [],
       columns: pendingColumns
    };

    runningJobsTable.bootstrapTable(runningOptions);
    completedJobsTable.bootstrapTable(completedOptions);
    pendingJobsTable.bootstrapTable(pendingOptions);

    $.ajax({
        url: 'ajax/get/jobs',
        dataType: 'json',
        success: function(response){
            var jobsData = response;
            loadTables(jobsData);
        }
    });


    function loadTables(jobsData){
        $.each(jobsData, function(i,v){
            if(i == "total"){
                return true;
            }
            $.each(v['rows'], function(j,k){
                if(i == "running")
                    runningJobsTable.bootstrapTable('append', k);
                if(i == "pending")
                    pendingJobsTable.bootstrapTable('append', k);
                if(i == "completed")
                    completedJobsTable.bootstrapTable('append', k);
            });
        });
    }
});
