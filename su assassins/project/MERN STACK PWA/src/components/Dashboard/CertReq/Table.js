import React from 'react';



export default function Table(props) {
    return (



        <div class="row">
        <div class="col-sm-12">
            <div class="panel panel-default card-view">
                <div class="panel-heading">
                    <div class="clearfix"></div>
                </div>
                <div class="panel-wrapper collapse in">
                    <div class="panel-body">
                        <div class="table-wrap">
                            <table id="footable_1" class="table" data-sorting="true">
                                <thead>
                                    <tr>
                                            <th className="th-th" data-name="id" data-breakpoints="xs" data-type="number">#</th>
                                            <th className="th-th" data-name="firstName">First Name</th>
                                            <th className="th-th" data-name="lastName">Last Name</th>
                                            <th className="th-th" data-name="jobTitle" data-breakpoints="xs">Job Title</th>
                                            <th className="th-th" data-name="startedOn" data-breakpoints="xs sm" data-type="date" data-format-string="MMMM Do YYYY">Started On</th>
                                            <th className="th-th" data-name="dob" data-breakpoints="xs sm md" data-type="date" data-format-string="MMMM Do YYYY">Date of Birth</th>
                                        </tr>
                                    </thead>

                                    {props.data.map((d, index) => {
                                        return (
                                            <tr>
                                                <td className="td-td" data-title="ID" data-breakpoints="xs">{index + 1}</td>
                                                <td className="td-td">{d.name}</td>
                                                <td className="td-td">{d.lastName}</td>
                                                <td className="td-td" data-title="Job Title" data-breakpoints="xs">{d.role}</td>
                                                <td className="td-td" data-title="Started On" data-breakpoints="xs sm">{new Date(d.start).toDateString().substr(-11)}</td>
                                                <td className="td-td" data-title="Date of Birth" data-breakpoints="xs sm md">{new Date(d.dob).toDateString().substr(-11)}</td>
                                            </tr>
                                        )
                                    })
                                    }
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}