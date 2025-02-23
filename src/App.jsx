import { useEffect, useState } from "react"
import Todoinput from "./components/Todoinput"
import Todolist from "./components/Todolist"


function App() {

  const [todos, setTodos ]= useState([])
  const [todovalue,setTodovalue]= useState('')

  function persistData(newlist){

    localStorage.setItem('todos',JSON.stringify({todos:newlist}))
  }



  function handleinput(newTodo){
    const newtodoslist =[...todos, newTodo]
    persistData(newtodoslist)
    setTodos(newtodoslist)
  }

  function handledelete(index){

    const newtodoslist= todos.filter((todo, todoIndex) =>
    {
      return todoIndex != index
    })
    persistData(newtodoslist)

    setTodos(newtodoslist)

  }

  function handleedit(index){
      const valuetobeedited = todos[index]
      setTodovalue(valuetobeedited)
      handledelete(index)
  }

  useEffect(()=> {
    if(!localStorage){
      return
    }

    let localtodos = localStorage.getItem('todos')
    if(!localtodos){
      return
    }

    localtodos= JSON.parse(localtodos).todos
    setTodos(localtodos)
    }, [])

  return (
    <>
     <main>
      <Todoinput todovalue={todovalue} setTodovalue={setTodovalue} handleinput={handleinput} />
      <Todolist handledelete={handledelete} handleedit={handleedit} todos={todos} />
     </main>
    </>
  )
}

export default App
