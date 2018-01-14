$(document).ready(function(){

    var table = $("#browse_table");
    table.bootstrapTable({
        search: true,
        pagination: true,
        sidePagination: 'server',
        url: 'ajax/get/items',
        classes: 'table table-striped table-hover',
        showRefresh: true,
        showColumns: true,
        columns : [{
           field: 'id',
           title: 'Id',
           sortable: true
        },
        {
           field: 'site_name',
           title: 'Site',
           sortable: true
        },
        {
           field: 'title',
           title: 'Title',
           sortable: true,
           cellStyle: function(value, row, index, field){
               return {
                   css: {"min-width":"150px"}
               }
           }
        },
        {
           field: 'content',
           title: 'Content',
           cellStyle: function(value, row, index, field){
               return {
                   css: {"min-width":"200px"}
               }
           }
        },
        {
           field: 'image',
           title: 'Image',
           formatter: function(value, row, index, field){
               return '<a href="' + value + '"><img src="' + value + '" style="width: 150px;  height: auto;"/></a>'
           }
        },
        {
           field: 'link',
           title: 'URL',
           formatter: function(value, row, index, field){
               return '<a href="' + value + '" title="' + row['title'] + '">' + value  + '</a>'
           },
           cellStyle: function(value, row, index, field){
               return {
                   css: {"font-size": "0.7em", "min-width": "150px"}
               }
           }
        },
        {
           field: 'newsdate',
           title: 'News Date',
           sortable: true
        },
        {
           field: 'datescraped',
           title: 'Scraping Date',
           sortable: true
        },
        {
           field: 'log_id',
           title: 'Log#',
           sortable: true
        }]
    });

});
