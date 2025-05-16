/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.return_order_form = publicWidget.Widget.extend({
    selector: '.parent-custom',
    events: {
        'click .list-btn-calendar': '_onClickCalendar',
        'click .list-btn-list': '_onClickList',
    },
    start: function () {
        this._super.apply(this, arguments);
        //If you want to Hide the calendar initially
        // this.$('#calendar').hide();
    },
    _onClickCalendar() { 
        $("#calendar-div").css("display", "block");
        $(".list-btn-calendar").css("background-color", "#8595A2");
        $(".list-btn-calendar").css("color", "white");
        $(".list-btn-list").css("background-color", "transparent");
        $(".list-btn-list").css("color", "black");

        // $('.o_portal_my_doc_table ').hide()
    },

    _onClickList() { 
        $("#calendar-div").css("display", "none");
        $(".list-btn-calendar").css("background-color", "transparent");
        $(".list-btn-calendar").css("color", "black");
        $(".list-btn-list").css("background-color", "#8595A2");
        $(".list-btn-list").css("color", "white");
        
        // $('.o_portal_my_doc_table ').show()
    },
})
;
 