import ReactDOM from 'react-dom'
import App from './js/app'
import './sass/index.scss'

window.onload = () => {
  const el = document.getElementById('content')
  const props = document.getElementById('content').getAttribute('props')
  ReactDOM.render((
    <App { ...(JSON.parse(props)) }/>
  ), el)
}