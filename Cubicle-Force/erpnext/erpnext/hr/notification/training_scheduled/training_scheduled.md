<table class="panel-header" border="0" cellpadding="0" cellspacing="0" width="100%">
    <tr height="10"></tr>
    <tr>
        <td width="15"></td>
        <td>
            <div class="text-medium text-muted">
                <span>{{_("Training Event:")}} {{ doc.event_name }}</span>
            </div>
        </td>
        <td width="15"></td>
    </tr>
    <tr height="10"></tr>
</table>

<table class="panel-body" border="0" cellpadding="0" cellspacing="0" width="100%">
    <tr height="10"></tr>
    <tr>
        <td width="15"></td>
        <td>
            <div>
                {{ doc.introduction }}
                <ul class="list-unstyled" style="line-height: 1.7">
                    <li>{{_("Event Location")}}: <b>{{ doc.location }}</b></li>
                    {% set start = frappe.utils.get_datetime(doc.start_time) %}
                    {% set end = frappe.utils.get_datetime(doc.end_time) %}
                    {% if start.date() == end.date() %}
                    <li>{{_("Date")}}: <b>{{ start.strftime("%A, %d %b %Y") }}</b></li>
                    <li>
                        {{_("Timing")}}: <b>{{ start.strftime("%I:%M %p") + ' to ' + end.strftime("%I:%M %p") }}</b>
                    </li>
                    {% else %}
                    <li>{{_("Start Time")}}: <b>{{ start.strftime("%A, %d %b %Y at %I:%M %p") }}</b>
                    </li>
                    <li>{{_("End Time")}}: <b>{{ end.strftime("%A, %d %b %Y at %I:%M %p") }}</b>
                    </li>
                    {% endif %}
                    <li>{{ _('Event Link') }}: {{ frappe.utils.get_link_to_form(doc.doctype, doc.name) }}</li>
                </ul>
            </div>
        </td>
        <td width="15"></td>
    </tr>
    <tr height="10"></tr>
</table>