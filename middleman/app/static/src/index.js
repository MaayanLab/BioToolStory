import ReactDOM from 'react-dom'
import App from './js/app'

window.onload = () => {
  const el = document.createElement('div')
  document.body.appendChild(el)

  ReactDOM.render((
    <App />
  ), el)
}