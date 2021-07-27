import * as React from 'react';
import { Lecture } from '../../model/lecture';
import { getAllLectures } from '../../services/lectures.service'
import { Scope, UserPermissions } from '../../services/permission.service';
import { CourseManageAssignmentsComponent } from './coursemanageassignment-list.component';


export interface CourseManageProps {
  // lectures: Array<Lecture>;
}

export class CourseManageComponent extends React.Component<CourseManageProps> {
  public lectures: number[];
  public state = {
    lectures: new Array<Lecture>()
  };

  constructor(props: CourseManageProps) {
    super(props);
    // this.state = {"lectures": props.lectures};
  }

  public async componentDidMount() {
    getAllLectures().subscribe(lectures => {
      console.log(lectures)
      this.setState(this.state.lectures = lectures)
    })
    await UserPermissions.loadPermissions();
  }

  public render() {
    return <div className="course-list">
      <h1>
        <p style={{textAlign:'center'}}>Course Management</p>
      </h1>
    {this.state.lectures.filter(el => UserPermissions.getScope(el) > Scope.student).map((el, index) => <CourseManageAssignmentsComponent lecture={el} title={el.name} open={index==0} />)}
    </div>
   
  }
}