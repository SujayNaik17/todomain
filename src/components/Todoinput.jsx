import { useState } from "react"

export default function Todoinput(props){

    // const {handleinput} = props
    const {todovalue,setTodovalue,handleinput}= props

    return (

            <header>
                <input value={todovalue} onChange={(e)=>{
                    setTodovalue(e.target.value)
                }}  placeholder="Enter Todo" />
                <button onClick={()=> {
                    handleinput(todovalue)
                    setTodovalue=('');
                }}>Add Todo</button>
                
            </header>



    )



}