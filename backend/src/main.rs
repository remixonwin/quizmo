use warp::Filter;
use ipfs_api_backend_hyper::{IpfsApi, IpfsClient};
use futures_util::TryStreamExt;
use std::sync::Arc;
use tokio::task;

#[tokio::main]
async fn main() {
    // Initialize IPFS client
    let client = Arc::new(IpfsClient::default());

    // Test IPFS connection by adding a simple file
    let data = "Hello, IPFS!";
    let _hash = match client.add(data.as_bytes()).await {
        Ok(res) => {
            println!("Added file to IPFS with hash: {}", res.hash);
            res.hash
        },
        Err(e) => {
            eprintln!("Failed to add file to IPFS: {:?}", e);
            eprintln!("Make sure you have a local IPFS node running.");
            return;
        }
    };

    // Serve the `frontend/pkg` directory at the root URL.
    let frontend = warp::fs::dir("../frontend/pkg");

    // Serve the index.html file at the root URL.
    let index = warp::path::end()
        .and(warp::fs::file("../frontend/pkg/index.html"));

    // Serve a default favicon
    let favicon = warp::path("favicon.ico")
        .and(warp::fs::file("../frontend/pkg/favicon.ico"));

    // API route to get the message from IPFS
    let ipfs_route = warp::path("ipfs")
        .and(warp::path::param())
        .and_then(move |hash: String| {
            let client = Arc::clone(&client);
            async move {
                task::spawn_blocking(move || {
                    let rt = tokio::runtime::Runtime::new().unwrap();
                    rt.block_on(async move {
                        match client.cat(&hash).map_ok(|chunk| chunk.to_vec()).try_concat().await {
                            Ok(data) => Ok(warp::reply::json(&String::from_utf8_lossy(&data).to_string())),
                            Err(_) => Err(warp::reject::not_found()),
                        }
                    })
                }).await.unwrap()
            }
        });

    // Combine the routes.
    let routes = index.or(frontend).or(favicon).or(ipfs_route);

    // Start the web server.
    warp::serve(routes)
        .run(([127, 0, 0, 1], 3030))
        .await;
}
