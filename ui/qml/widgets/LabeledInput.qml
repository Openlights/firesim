import QtQuick 1.0

Column {
    id: labeledInput

    property variant key
    property variant value

    signal changed

    width: 60
    height: 16

    Row {
        anchors { right: parent.right }
        anchors { leftMargin: 2; rightMargin: 2 }
        Text { color: "#eeeeee"; text: key + ": "}
        Rectangle {
            height: 16
            width: 25
            color: "#444444"
            TextInput {
                anchors.fill: parent
                anchors { leftMargin: 2; rightMargin: 2 }
                color: "#eeeeee"
                text: value
                selectByMouse: true
            }
        }
    }

    //states: State {
    //    name: "pressed"; when: mouseArea.pressed == true
    //    PropertyChanges { target: shade; opacity: .4 }
    //}
}