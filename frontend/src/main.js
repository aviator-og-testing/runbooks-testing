/**
 * runbooks_testing Frontend
 *
 * Built with Backbone.js - a lightweight MV* framework.
 * NOTE: Backbone.js is legacy software (last major release 2016).
 * Consider migrating to React, Vue, or Svelte for new features.
 */

/* global Backbone, _, $, moment */

(function () {
  "use strict";

  var API_BASE = "/api";

  // ============================================================
  // Utility Functions (using moment.js - also legacy)
  // TODO: Migrate to date-fns or native Intl.DateTimeFormat
  // ============================================================

  window.formatTimestamp = function (date) {
    return moment(date).format("MMMM Do YYYY, h:mm:ss a");
  };

  window.getRelativeTime = function (date) {
    return moment(date).fromNow();
  };

  window.formatShortDate = function (date) {
    return moment(date).format("MM/DD/YYYY");
  };

  window.formatISODate = function (date) {
    return moment(date).toISOString();
  };

  window.getDayOfWeek = function (date) {
    return moment(date).format("dddd");
  };

  // ============================================================
  // Models
  // ============================================================

  var User = Backbone.Model.extend({
    defaults: {
      username: "",
      email: "",
      created_at: null,
    },

    getFormattedCreatedAt: function () {
      return this.get("created_at")
        ? window.formatTimestamp(this.get("created_at"))
        : "Unknown";
    },

    getRelativeCreatedAt: function () {
      return this.get("created_at")
        ? window.getRelativeTime(this.get("created_at"))
        : "Unknown";
    },

    validate: function (attrs) {
      if (!attrs.username || attrs.username.trim() === "") {
        return "Username is required";
      }
      if (!attrs.email || attrs.email.indexOf("@") === -1) {
        return "A valid email is required";
      }
    },
  });

  var Item = Backbone.Model.extend({
    defaults: {
      name: "",
      description: null,
      updated_at: null,
    },

    getFormattedUpdatedAt: function () {
      return this.get("updated_at")
        ? window.formatTimestamp(this.get("updated_at"))
        : "Never";
    },
  });

  // ============================================================
  // Collections
  // ============================================================

  var UserCollection = Backbone.Collection.extend({
    model: User,
    url: API_BASE + "/users",

    comparator: function (model) {
      return -moment(model.get("created_at")).valueOf();
    },
  });

  var ItemCollection = Backbone.Collection.extend({
    model: Item,
    url: API_BASE + "/items",
  });

  // ============================================================
  // Views
  // ============================================================

  var HomeView = Backbone.View.extend({
    template: _.template($("#home-template").html()),

    render: function () {
      this.$el.html(this.template());
      return this;
    },
  });

  var UsersView = Backbone.View.extend({
    template: _.template($("#users-template").html()),

    initialize: function () {
      this.collection = new UserCollection();
      this.listenTo(this.collection, "sync", this.render);
      this.listenTo(this.collection, "error", this.onFetchError);
      this.collection.fetch();
    },

    render: function () {
      var users = this.collection.map(function (user) {
        return {
          username: user.get("username"),
          email: user.get("email"),
          created: user.getFormattedCreatedAt(),
          relative: user.getRelativeCreatedAt(),
          dayOfWeek: user.get("created_at")
            ? window.getDayOfWeek(user.get("created_at"))
            : "",
        };
      });
      this.$el.html(this.template({ users: users }));
      return this;
    },

    onFetchError: function (collection, response) {
      this.$el.html(
        '<div class="error">Failed to load users: ' +
          _.escape(response.statusText) +
          "</div>",
      );
    },
  });

  var UserFormView = Backbone.View.extend({
    template: _.template($("#user-form-template").html()),

    events: {
      "submit #create-user-form": "onSubmit",
    },

    initialize: function () {
      this.collection = new UserCollection();
    },

    render: function () {
      this.$el.html(this.template());
      return this;
    },

    onSubmit: function (e) {
      e.preventDefault();
      var self = this;

      var username = this.$("#username-input").val().trim();
      var email = this.$("#email-input").val().trim();

      if (!username) {
        this.showError("Username is required.");
        return;
      }
      if (!email || email.indexOf("@") === -1) {
        this.showError("A valid email address is required.");
        return;
      }

      $.ajax({
        url: API_BASE + "/users",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ username: username, email: email }),
        success: function (data) {
          self.showSuccess(
            "User created: " +
              _.escape(data.username) +
              " at " +
              window.formatTimestamp(data.created_at),
          );
          self.$("#create-user-form")[0].reset();
        },
        error: function (xhr) {
          var msg = "Failed to create user";
          if (xhr.responseJSON && xhr.responseJSON.error) {
            msg = xhr.responseJSON.error;
          }
          self.showError(msg);
        },
      });
    },

    showError: function (msg) {
      this.$(".form-message")
        .html('<span class="error">' + _.escape(msg) + "</span>")
        .show();
    },

    showSuccess: function (msg) {
      this.$(".form-message")
        .html('<span class="success">' + msg + "</span>")
        .show();
    },
  });

  var UserDetailView = Backbone.View.extend({
    template: _.template($("#user-detail-template").html()),

    initialize: function (options) {
      this.userId = options.userId;
      this.model = new User({ id: this.userId });
    },

    render: function () {
      var self = this;
      this.$el.html("<p>Loading...</p>");

      $.ajax({
        url: API_BASE + "/users/" + this.userId,
        type: "GET",
        dataType: "json",
        success: function (data) {
          self.model.set(data);
          self.$el.html(
            self.template({
              username: self.model.get("username"),
              email: self.model.get("email"),
              created: self.model.getFormattedCreatedAt(),
              relative: self.model.getRelativeCreatedAt(),
              shortDate: self.model.get("created_at")
                ? window.formatShortDate(self.model.get("created_at"))
                : "N/A",
            }),
          );
        },
        error: function (xhr) {
          self.$el.html(
            '<div class="error">Failed to load user: ' +
              _.escape(xhr.statusText) +
              "</div>",
          );
        },
      });

      return this;
    },
  });

  var ItemsView = Backbone.View.extend({
    template: _.template($("#items-template").html()),

    initialize: function () {
      this.collection = new ItemCollection();
      this.listenTo(this.collection, "sync", this.render);
      this.listenTo(this.collection, "error", this.onFetchError);
      this.collection.fetch();
    },

    render: function () {
      var items = this.collection.map(function (item) {
        return {
          name: item.get("name"),
          description: item.get("description"),
          updated: item.getFormattedUpdatedAt(),
        };
      });
      this.$el.html(this.template({ items: items }));
      return this;
    },

    onFetchError: function (collection, response) {
      this.$el.html(
        '<div class="error">Failed to load items: ' +
          _.escape(response.statusText) +
          "</div>",
      );
    },
  });

  // ============================================================
  // Router
  // Using Backbone.Router for hash-based navigation
  // This was the standard before HTML5 History API adoption
  // ============================================================

  var AppRouter = Backbone.Router.extend({
    routes: {
      "": "home",
      users: "users",
      "users/new": "newUser",
      "users/:id": "userDetail",
      items: "items",
      "*path": "notFound",
    },

    initialize: function () {
      this.$app = $("#app");
    },

    home: function () {
      var view = new HomeView();
      this.$app.html(view.render().$el);
    },

    users: function () {
      var view = new UsersView();
      this.$app.html(view.render().$el);
    },

    newUser: function () {
      var view = new UserFormView();
      this.$app.html(view.render().$el);
    },

    userDetail: function (id) {
      var view = new UserDetailView({ userId: id });
      this.$app.html(view.render().$el);
    },

    items: function () {
      var view = new ItemsView();
      this.$app.html(view.render().$el);
    },

    notFound: function (path) {
      this.$app.html("<h1>Hello " + _.escape(path) + "</h1>");
    },
  });

  // ============================================================
  // Application Bootstrap
  // ============================================================

  $(document).ready(function () {
    new AppRouter();
    Backbone.history.start();
  });
})();
