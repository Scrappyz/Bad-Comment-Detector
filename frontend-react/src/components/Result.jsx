import React from "react";
import PropTypes from "prop-types";

function Result(props) {

    const style = {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "Arial, Helvetica, sans-serif",
        fontWeight: "bold",
        fontSize: "36px",
        color: props.textColor
    }

    return (
        <div style={style}>
          {props.text}
        </div>
    )
}

Result.PropTypes = {
    text: PropTypes.string,
    textColor: PropTypes.string
}

Result.defaultProps = {
    text: null,
    textColor: "green"
}

export default Result;