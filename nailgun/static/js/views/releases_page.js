define(
[
    'views/common',
    'views/dialogs',
    'text!templates/release/list.html'
],
function(commonViews, dialogViews, releasesListTemplate) {
    'use strict';

    var ReleasesPage = commonViews.Page.extend({
        navbarActiveElement: 'releases',
        breadcrumbsPath: [['Home', '#'], 'Releases'],
        title: 'Releases',
        updateInterval: 3000,
        template: _.template(releasesListTemplate),
        'events': {
            'click .btn-rhel-setup': 'showRhelLicenseCredentials'
        },
        showRhelLicenseCredentials: function() {
            var dialog = new dialogViews.RhelLicenseDialog({model: this.model});
            this.registerSubView(dialog);
            dialog.render();
        },
        scheduleUpdate: function() {
            if (app.navbar.task('download', 'running')) {
                this.registerDeferred($.timeout(this.updateInterval).done(_.bind(this.update, this)));
            }
        },
        update: function() {
            var downloadTask = app.navbar.task('download', 'running');
            if (downloadTask) {
                this.renderProgress(downloadTask.get('release'));
                this.registerDeferred(downloadTask.fetch().done(_.bind(function() {
                    if (downloadTask.get('status') != 'running') {
                        this.collection.fetch();
                    }
                }, this)).always(_.bind(this.scheduleUpdate, this)));
            }
        },
        renderProgress: function(release){
            var row = this.$('.releases-table td[data-release=' + release + ']');
            row.find('.btn-rhel-setup, #download_progress').toggle();
            row.find('.bar').css('width', this.progress+'%');
        },
        initialize: function() {
            this.collection.on('sync', this.render);
            this.scheduleUpdate();
        },
        render: function() {
            this.$el.html(this.template({releases: this.collection}));
            return this;
        }
    });

    return ReleasesPage;
});
