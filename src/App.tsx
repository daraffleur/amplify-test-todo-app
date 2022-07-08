import { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { withAuthenticator } from "@aws-amplify/ui-react";
import { Auth, API } from "aws-amplify";

interface ITask {
  id: string;
  description: string;
  user: string;
}

function App() {

  const [user, setUser] = useState<any>(null);
  const [formValue, setFormValue] = useState<string>("");
  const [tasks, setTasks] = useState<ITask[]>([]);
  const [refresh, setRefresh] = useState(true);

  const handleLogout = async (): Promise<void> => {
    try {
      await Auth.signOut();
    } catch (error) {
      console.error(error)
    }
  }

  const fetchUser = async (): Promise<void> => {
    try {
      const userResponse = await Auth.currentAuthenticatedUser();
      setUser(userResponse);
      return userResponse;
    } catch (error) {
      console.error(error)
    }
  }

  const userEmail = user ? user.attributes.email : "test@com";

  useEffect(() => {

    const getTasks = async () => {
      const userres: any = await fetchUser();

      const response = await API.get("tasksapi", `/tasks/${userres?.attributes.email}`, {})
      setTasks(response.data)
      setRefresh(false);
    }
    if (refresh) {
      getTasks();
    }
  }, [refresh, userEmail])

  console.log("USER: ", user);

  const handleFormChange = (e: any) => {
    setFormValue(e.target.value);
  }

  const handleCreateTask = async (): Promise<void> => {
    await API.post("tasksapi", "/tasks/new", { body: { description: formValue, user: user.attributes.email } })
      .then((response) => setRefresh(true))
      .catch((err) => console.error(err))
  }


  return (
    <div>
      <button onClick={handleLogout}>Logout</button>
      {user ? <p>HI, {user.attributes.email}</p> : null}
      <br />
      <h1>Create Task</h1>
      <input type="text" name="desc" placeholder='Desc' onChange={handleFormChange} value={formValue}></input>
      <button type="submit" onClick={handleCreateTask}>Submit</button>

      <h1>My Tasks</h1>
      <ul>
        {tasks.length > 0 ?
          tasks.map((task: ITask, i: number) => {
            return <li key={i}>{task.description}</li>
          })
          : <p>No tasks</p>}

      </ul>

    </div>
  );
}

export default withAuthenticator(App);
