import QtQuick 2.12
import "../theme"

Rectangle {
    id: dock
    signal actionTriggered(int index, string label)
    // [TEST-BUTTON] Test 버튼은 tab과 별개로 눌림/해제 상태를 가진다.
    property bool testActive: false

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#141c26" }
        GradientStop { position: 1.0; color: "#0a1018" }
    }

    Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: Theme.borderDefault }
    Canvas {
        anchors.top: parent.top; anchors.topMargin: 1; width: parent.width; height: 2
        onPaint: {
            var ctx = getContext("2d"); ctx.reset()
            var g = ctx.createLinearGradient(0, 0, width, 0)
            g.addColorStop(0.0, "transparent"); g.addColorStop(0.3, "rgba(89,192,205,0.1)")
            g.addColorStop(0.5, "rgba(89,192,205,0.2)"); g.addColorStop(0.7, "rgba(89,192,205,0.1)")
            g.addColorStop(1.0, "transparent"); ctx.fillStyle = g; ctx.fillRect(0, 0, width, height)
        }
    }

    Row {
        anchors.centerIn: parent; spacing: 10

        Repeater {
            // 하단 dock은 화면 전환 또는 보조 기능 호출을 위한 빠른 액션 모음이다.
            model: [
                { icon: "\u{1F697}", label: "Vehicle" },
                { icon: "\u{1F9ED}", label: "Navigation" },
                { icon: "\u{1F441}", label: "Perception" },
                { icon: "\u{1F3AC}", label: "Scenario" },
                { icon: "\u{1F4CB}", label: "History" },
                { icon: "\u2699",    label: "Settings" },
                // [TEST-BUTTON] CAN 테스트 전송용으로 추가한 버튼
                { icon: "\u{1F9EA}", label: "Test" }
            ]
            delegate: Rectangle {
                width: 120; height: 48; radius: Theme.radiusMd
                property bool highlighted: modelData.label === "Test" ? dock.testActive : app.activeTab === index
                color: highlighted ? Theme.rgba("#59c0cd", 0.12) : "transparent"
                border.color: highlighted ? Theme.rgba("#59c0cd", 0.3) : "transparent"; border.width: 1

                Row {
                    anchors.centerIn: parent; spacing: 6
                    Text { text: modelData.icon; font.pixelSize: 18; color: highlighted ? Theme.accentCyan : Theme.textMuted; anchors.verticalCenter: parent.verticalCenter }
                    Text { text: modelData.label; font.pixelSize: Theme.fontMd; font.bold: highlighted; color: highlighted ? Theme.accentCyan : Theme.textSecondary; anchors.verticalCenter: parent.verticalCenter }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    // 실제 동작 분기는 main.qml의 onActionTriggered에서 처리한다.
                    onClicked: dock.actionTriggered(index, modelData.label)
                }
            }
        }
    }

    Text {
        anchors.right: parent.right; anchors.rightMargin: 22; anchors.verticalCenter: parent.verticalCenter
        text: "TOPST"; color: Theme.textMuted; font.pixelSize: Theme.fontMd; font.bold: true; font.letterSpacing: 4
    }
}
