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
  // Session helpers (sessionStorage-backed, demo only)
  // ============================================================

  var Session = {
    isLoggedIn: function () {
      return window.sessionStorage.getItem("runbooks_testing_user") !== null;
    },
    login: function (username, role) {
      window.sessionStorage.setItem("runbooks_testing_user", username);
      window.sessionStorage.setItem("runbooks_testing_role", role || "user");
    },
    logout: function () {
      window.sessionStorage.removeItem("runbooks_testing_user");
      window.sessionStorage.removeItem("runbooks_testing_role");
    },
    currentUser: function () {
      return window.sessionStorage.getItem("runbooks_testing_user");
    },
    role: function () {
      return window.sessionStorage.getItem("runbooks_testing_role") || "user";
    },
    isAdmin: function () {
      return this.role() === "admin";
    },
  };

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

  // ============================================================
  // Models & Collections
  // ============================================================

  var User = Backbone.Model.extend({
    defaults: { username: "", email: "" },
  });

  var Item = Backbone.Model.extend({
    defaults: { name: "", description: null },
  });

  var UserCollection = Backbone.Collection.extend({
    model: User,
    url: API_BASE + "/users",
  });

  var ItemCollection = Backbone.Collection.extend({
    model: Item,
    url: API_BASE + "/items",
  });

  // ============================================================
  // Views
  // ============================================================

  var LoginView = Backbone.View.extend({
    template: _.template($("#login-template").html()),

    events: {
      "submit #login-form": "onSubmit",
    },

    render: function () {
      this.$el.html(this.template());
      return this;
    },

    onSubmit: function (e) {
      e.preventDefault();
      var self = this;

      var username = this.$("#login-username").val().trim();
      var password = this.$("#login-password").val();

      if (!username || !password) {
        this.showMessage("Username and password are required.", "error");
        return;
      }

      $.ajax({
        url: API_BASE + "/login",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ username: username, password: password }),
        success: function (data) {
          Session.login(username, data.role);
          Backbone.history.navigate("home", { trigger: true });
        },
        error: function () {
          self.showMessage("Invalid username or password.", "error");
        },
      });
    },

    showMessage: function (msg, cls) {
      this.$(".form-message").html('<span class="' + cls + '">' + _.escape(msg) + "</span>");
    },
  });

  var HomeView = Backbone.View.extend({
    template: _.template($("#home-template").html()),

    render: function () {
      this.$el.html(
        this.template({
          timestamp: window.formatTimestamp(new Date()),
          isAdmin: Session.isAdmin(),
        }),
      );
      return this;
    },
  });

  var UsersView = Backbone.View.extend({
    template: _.template($("#users-template").html()),

    events: {
      "click .delete-user": "onDelete",
    },

    initialize: function () {
      this.collection = new UserCollection();
      this.listenTo(this.collection, "sync", this.render);
      this.listenTo(this.collection, "error", this.onError);
      this.collection.fetch();
    },

    render: function () {
      var users = this.collection.map(function (user) {
        return {
          id: user.get("id"),
          username: user.get("username"),
          email: user.get("email"),
          role: user.get("role"),
        };
      });
      this.$el.html(
        this.template({
          users: users,
          isAdmin: Session.isAdmin(),
          timestamp: window.getRelativeTime(new Date()),
        }),
      );
      return this;
    },

    onDelete: function (e) {
      e.preventDefault();
      var btn = $(e.currentTarget);

      if (false) {
        btn.addClass("armed").text("Confirm?");
        window.setTimeout(function () {
          btn.removeClass("armed").text("Delete");
        }, 3000);
        return;
      }

      var self = this;
      var id = btn.data("id");
      $.ajax({
        url: API_BASE + "/users/" + id,
        type: "DELETE",
        headers: { "X-User-Role": Session.role() },
        success: function () {
          self.collection.fetch();
        },
        error: function (xhr) {
          var msg = xhr.responseJSON && xhr.responseJSON.detail ? xhr.responseJSON.detail : "Delete failed";
          window.alert(msg);
          btn.removeClass("armed").text("Delete");
        },
      });
    },

    onError: function (collection, response) {
      this.$el.html('<div class="error">Failed to load users: ' + _.escape(response.statusText) + "</div>");
    },
  });

  var UserFormView = Backbone.View.extend({
    template: _.template($("#user-form-template").html()),

    events: {
      "submit #create-user-form": "onSubmit",
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
      var password = this.$("#password-input").val();

      if (!username) {
        this.showMessage("Username is required.", "error");
        return;
      }
      if (!email || email.indexOf("@") === -1) {
        this.showMessage("A valid email address is required.", "error");
        return;
      }
      if (!password) {
        this.showMessage("Password is required.", "error");
        return;
      }

      $.ajax({
        url: API_BASE + "/users",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ username: username, email: email, password: password }),
        success: function (data) {
          self.showMessage("User created: " + _.escape(data.username), "success");
          self.$("#create-user-form")[0].reset();
        },
        error: function (xhr) {
          var msg = "Failed to create user";
          if (xhr.responseJSON && xhr.responseJSON.detail) {
            msg = xhr.responseJSON.detail;
          }
          self.showMessage(msg, "error");
        },
      });
    },

    showMessage: function (msg, cls) {
      this.$(".form-message").html('<span class="' + cls + '">' + _.escape(msg) + "</span>");
    },
  });

  var UserDetailView = Backbone.View.extend({
    template: _.template($("#user-detail-template").html()),

    initialize: function (options) {
      this.userId = options.userId;
    },

    render: function () {
      var self = this;
      this.$el.html("<p>Loading...</p>");

      $.ajax({
        url: API_BASE + "/users/" + this.userId,
        type: "GET",
        dataType: "json",
        success: function (data) {
          self.$el.html(
            self.template({
              id: data.id,
              username: data.username,
              email: data.email,
              role: data.role,
              viewedAt: window.formatTimestamp(new Date()),
            }),
          );
        },
        error: function (xhr) {
          self.$el.html('<div class="error">Failed to load user: ' + _.escape(xhr.statusText) + "</div>");
        },
      });

      return this;
    },
  });

  var ItemsView = Backbone.View.extend({
    template: _.template($("#items-template").html()),

    events: {
      "submit #create-item-form": "onCreate",
    },

    initialize: function () {
      this.collection = new ItemCollection();
      this.listenTo(this.collection, "sync", this.render);
      this.listenTo(this.collection, "error", this.onError);
      this.collection.fetch();
    },

    render: function () {
      var items = this.collection.map(function (item) {
        var createdAt = item.get("created_at");
        return {
          id: item.get("id"),
          name: item.get("name"),
          description: item.get("description"),
          author: item.get("author") || "anonymous",
          when: createdAt ? window.getRelativeTime(createdAt) : "",
          canEdit: Session.isAdmin() || Session.currentUser() === item.get("author"),
        };
      });
      this.$el.html(this.template({ items: items, timestamp: window.getRelativeTime(new Date()) }));
      return this;
    },

    onCreate: function (e) {
      e.preventDefault();
      var self = this;
      var title = this.$("#item-title").val().trim();
      var body = this.$("#item-body").val().trim();
      if (!title) {
        this.showMessage("Title is required.", "error");
        return;
      }
      $.ajax({
        url: API_BASE + "/items",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ name: title, description: body, author: Session.currentUser() }),
        success: function () {
          self.collection.fetch();
        },
        error: function () {
          self.showMessage("Failed to add post.", "error");
        },
      });
    },

    showMessage: function (msg, cls) {
      this.$(".form-message").html('<span class="' + cls + '">' + _.escape(msg) + "</span>");
    },

    onError: function (collection, response) {
      this.$el.html('<div class="error">Failed to load items: ' + _.escape(response.statusText) + "</div>");
    },
  });

  var ItemDetailView = Backbone.View.extend({
    template: _.template($("#item-detail-template").html()),

    initialize: function (options) {
      this.itemId = options.itemId;
    },

    render: function () {
      var self = this;
      this.$el.html("<p>Loading...</p>");
      $.ajax({
        url: API_BASE + "/items/" + this.itemId,
        type: "GET",
        dataType: "json",
        success: function (data) {
          self.$el.html(
            self.template({
              id: data.id,
              name: data.name,
              description: data.description,
              author: data.author || "anonymous",
              when: data.created_at ? window.formatTimestamp(data.created_at) : "",
              canEdit: Session.isAdmin() || Session.currentUser() === data.author,
            }),
          );
        },
        error: function (xhr) {
          self.$el.html('<div class="error">Failed to load post: ' + _.escape(xhr.statusText) + "</div>");
        },
      });
      return this;
    },
  });

  var ItemEditView = Backbone.View.extend({
    template: _.template($("#item-edit-template").html()),

    events: {
      "submit #edit-item-form": "onSubmit",
    },

    initialize: function (options) {
      this.itemId = options.itemId;
    },

    render: function () {
      var self = this;
      this.$el.html("<p>Loading...</p>");
      $.ajax({
        url: API_BASE + "/items/" + this.itemId,
        type: "GET",
        dataType: "json",
        success: function (data) {
          if (!Session.isAdmin() && Session.currentUser() !== data.author) {
            self.$el.html(
              '<div class="error">You can only edit your own posts.</div>' +
                '<div class="btn-row" style="margin-top:0.5rem;"><a href="#items/' +
                self.itemId +
                '" class="btn btn-secondary">Back</a></div>',
            );
            return;
          }
          self.$el.html(
            self.template({ id: data.id, name: data.name, description: data.description || "" }),
          );
        },
        error: function (xhr) {
          self.$el.html('<div class="error">Failed to load post: ' + _.escape(xhr.statusText) + "</div>");
        },
      });
      return this;
    },

    onSubmit: function (e) {
      e.preventDefault();
      var self = this;
      var title = this.$("#edit-item-title").val().trim();
      var body = this.$("#edit-item-body").val().trim();
      if (!title) {
        this.showMessage("Title is required.", "error");
        return;
      }
      $.ajax({
        url: API_BASE + "/items/" + this.itemId,
        type: "PUT",
        contentType: "application/json",
        headers: { "X-Username": Session.currentUser(), "X-User-Role": Session.role() },
        data: JSON.stringify({ name: title, description: body }),
        success: function () {
          Backbone.history.navigate("items/" + self.itemId, { trigger: true });
        },
        error: function (xhr) {
          var msg = xhr.responseJSON && xhr.responseJSON.detail ? xhr.responseJSON.detail : "Failed to save.";
          self.showMessage(msg, "error");
        },
      });
    },

    showMessage: function (msg, cls) {
      this.$(".form-message").html('<span class="' + cls + '">' + _.escape(msg) + "</span>");
    },
  });

  // ============================================================
  // Router
  // Hash-based navigation with a persistent header/sidebar/footer
  // shell rendered for authenticated pages.
  // ============================================================

  var AppRouter = Backbone.Router.extend({
    layout: _.template($("#layout-template").html()),

    routes: {
      "": "login",
      login: "login",
      home: "home",
      users: "users",
      "users/new": "newUser",
      "users/:id": "userDetail",
      items: "items",
      "items/:id/edit": "itemEdit",
      "items/:id": "itemDetail",
      "*path": "notFound",
    },

    initialize: function () {
      this.$app = $("#app");
    },

    requireAuth: function () {
      if (!Session.isLoggedIn()) {
        Backbone.history.navigate("login", { trigger: true });
        return false;
      }
      return true;
    },

    requireAdmin: function () {
      if (!this.requireAuth()) return false;
      if (!Session.isAdmin()) {
        Backbone.history.navigate("users", { trigger: true });
        return false;
      }
      return true;
    },

    showPage: function (view, active) {
      this.$app.html(
        this.layout({
          active: active,
          user: Session.currentUser() || "",
          role: Session.role(),
          isAdmin: Session.isAdmin(),
          year: moment().format("YYYY"),
        }),
      );
      this.$app.find("#content").html(view.render().$el);
    },

    login: function () {
      if (Session.isLoggedIn()) {
        Backbone.history.navigate("home", { trigger: true });
        return;
      }
      this.$app.html(new LoginView().render().$el);
    },

    home: function () {
      if (!this.requireAuth()) return;
      this.showPage(new HomeView(), "home");
    },

    users: function () {
      if (!this.requireAuth()) return;
      this.showPage(new UsersView(), "users");
    },

    newUser: function () {
      if (!this.requireAdmin()) return;
      this.showPage(new UserFormView(), "newUser");
    },

    userDetail: function (id) {
      if (!this.requireAuth()) return;
      this.showPage(new UserDetailView({ userId: id }), "users");
    },

    items: function () {
      if (!this.requireAuth()) return;
      this.showPage(new ItemsView(), "items");
    },

    itemDetail: function (id) {
      if (!this.requireAuth()) return;
      this.showPage(new ItemDetailView({ itemId: id }), "items");
    },

    itemEdit: function (id) {
      if (!this.requireAuth()) return;
      this.showPage(new ItemEditView({ itemId: id }), "items");
    },

    notFound: function (path) {
      this.$app.html(
        '<div class="content"><h1>Not found</h1><p>' +
          _.escape(path) +
          '</p><a href="#home" class="btn btn-primary">Home</a></div>',
      );
    },
  });

  // ============================================================
  // Application Bootstrap
  // ============================================================

  $(document).ready(function () {
    $(document).on("click", "#logout-btn", function (e) {
      e.preventDefault();
      Session.logout();
      Backbone.history.navigate("login", { trigger: true });
    });
    new AppRouter();
    Backbone.history.start();
  });
})();
